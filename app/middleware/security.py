"""
安全头中间件
添加安全相关的 HTTP 头
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    def __init__(
        self,
        app,
        enable_hsts: bool = True,
        enable_csp: bool = True,
        enable_xss_protection: bool = True,
        enable_content_type_options: bool = True,
        enable_frame_options: bool = True,
        enable_referrer_policy: bool = True,
    ):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.enable_csp = enable_csp
        self.enable_xss_protection = enable_xss_protection
        self.enable_content_type_options = enable_content_type_options
        self.enable_frame_options = enable_frame_options
        self.enable_referrer_policy = enable_referrer_policy
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # HSTS - 强制 HTTPS
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP - 内容安全策略
        if self.enable_csp:
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://api.github.com https://api.notion.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
            response.headers["Content-Security-Policy"] = csp_policy
        
        # XSS 保护
        if self.enable_xss_protection:
            response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 内容类型选项
        if self.enable_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 帧选项
        if self.enable_frame_options:
            response.headers["X-Frame-Options"] = "DENY"
        
        # 引用策略
        if self.enable_referrer_policy:
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 移除服务器信息
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


class InputSanitizer:
    """输入净化器"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """净化字符串输入"""
        if not isinstance(value, str):
            return str(value)
        
        # 移除控制字符
        value = ''.join(char for char in value if char.isprintable() or char.isspace())
        
        # 限制长度
        if len(value) > max_length:
            value = value[:max_length]
        
        return value.strip()
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """净化路径输入"""
        if not isinstance(path, str):
            return ""
        
        # 移除路径遍历尝试
        import re
        path = re.sub(r'\.\./+', '', path)
        path = re.sub(r'//+', '/', path)
        
        # 移除空字节
        path = path.replace('\x00', '')
        
        return path.strip()
    
    @staticmethod
    def sanitize_dict(data: dict, max_depth: int = 10) -> dict:
        """净化字典输入"""
        if not isinstance(data, dict):
            return {}
        
        def _sanitize(obj, depth=0):
            if depth > max_depth:
                return None
            
            if isinstance(obj, str):
                return InputSanitizer.sanitize_string(obj)
            elif isinstance(obj, dict):
                return {
                    InputSanitizer.sanitize_string(str(k)): _sanitize(v, depth + 1)
                    for k, v in obj.items()
                }
            elif isinstance(obj, (list, tuple)):
                return [_sanitize(item, depth + 1) for item in obj]
            elif isinstance(obj, (int, float, bool)):
                return obj
            else:
                return str(obj)
        
        return _sanitize(data) or {}


class RequestValidator:
    """请求验证器"""
    
    @staticmethod
    def validate_json_body(body: dict, required_fields: list = None) -> dict:
        """验证 JSON 请求体"""
        if not isinstance(body, dict):
            raise ValueError("Request body must be a JSON object")
        
        # 检查必需字段
        if required_fields:
            for field in required_fields:
                if field not in body:
                    raise ValueError(f"Missing required field: {field}")
        
        # 净化输入
        return InputSanitizer.sanitize_dict(body)
    
    @staticmethod
    def validate_pagination(params: dict) -> dict:
        """验证分页参数"""
        page = params.get("page", 1)
        per_page = params.get("per_page", 30)
        
        if not isinstance(page, int) or page < 1:
            page = 1
        
        if not isinstance(per_page, int) or per_page < 1:
            per_page = 30
        elif per_page > 100:
            per_page = 100
        
        return {"page": page, "per_page": per_page}
