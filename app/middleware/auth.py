"""
API 认证中间件
提供 JWT 和 API Key 认证
"""

import os
import secrets
import time
import hashlib
import hmac
from typing import Optional, Dict, Any
from functools import wraps

from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from datetime import datetime, timedelta

from ..utils.logger import get_logger

logger = get_logger(__name__)

# 配置
_app_env = os.environ.get("APP_ENV", "development")
_jwt_secret = os.environ.get("JWT_SECRET_KEY")

if _jwt_secret:
    SECRET_KEY = _jwt_secret
elif _app_env.lower() == "production":
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable is required in production. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
    )
else:
    logger.warning(
        "JWT_SECRET_KEY not set — using ephemeral random key (development only). "
        "Set JWT_SECRET_KEY in your .env file for persistent tokens."
    )
    SECRET_KEY = secrets.token_urlsafe(64)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API Key 配置
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
api_keys: Dict[str, Dict[str, Any]] = {}


def init_api_keys():
    """初始化 API Keys 从环境变量"""
    global api_keys
    api_keys_env = os.environ.get("API_KEYS", "")
    if api_keys_env:
        for key_pair in api_keys_env.split(","):
            if ":" in key_pair:
                key, name = key_pair.split(":", 1)
                api_keys[key.strip()] = {
                    "name": name.strip(),
                    "created_at": datetime.now().isoformat()
                }


# 初始化 API Keys
init_api_keys()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """获取当前认证用户"""
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    return payload


async def verify_api_key(
    api_key: Optional[str] = Security(API_KEY_HEADER)
) -> Optional[Dict[str, Any]]:
    """验证 API Key"""
    if api_key is None:
        return None
    
    if api_key in api_keys:
        return api_keys[api_key]
    
    return None


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    api_key: Optional[str] = Security(API_KEY_HEADER)
) -> Dict[str, Any]:
    """要求认证 - 支持 JWT 或 API Key"""
    # 尝试 JWT 认证
    if credentials:
        payload = verify_token(credentials.credentials)
        if payload:
            return {"auth_type": "jwt", "user": payload}
    
    # 尝试 API Key 认证
    if api_key:
        key_info = api_keys.get(api_key)
        if key_info:
            return {"auth_type": "api_key", "key_info": key_info}
    
    # 认证失败
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def optional_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    api_key: Optional[str] = Security(API_KEY_HEADER)
) -> Optional[Dict[str, Any]]:
    """可选认证 - 不要求但会验证"""
    # 尝试 JWT 认证
    if credentials:
        payload = verify_token(credentials.credentials)
        if payload:
            return {"auth_type": "jwt", "user": payload}
    
    # 尝试 API Key 认证
    if api_key:
        key_info = api_keys.get(api_key)
        if key_info:
            return {"auth_type": "api_key", "key_info": key_info}
    
    return None


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        minute_ago = now - 60
        
        # 清理旧记录
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > minute_ago
            ]
        else:
            self.requests[client_id] = []
        
        # 检查限制
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # 记录请求
        self.requests[client_id].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter()


async def check_rate_limit(request: Request):
    """检查速率限制"""
    client_id = request.client.host
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
