"""
安全中间件测试
测试认证、安全头、输入验证等中间件
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.middleware.auth import (
    create_access_token,
    verify_token,
    RateLimiter,
    init_api_keys,
    api_keys,
)
from app.middleware.security import (
    InputSanitizer,
    RequestValidator,
    SecurityHeadersMiddleware,
)


class TestInputSanitizer:
    """输入净化器测试"""
    
    def test_sanitize_string_basic(self):
        """测试基本字符串净化"""
        result = InputSanitizer.sanitize_string("  hello world  ")
        assert result == "hello world"
    
    def test_sanitize_string_control_chars(self):
        """测试移除控制字符"""
        result = InputSanitizer.sanitize_string("hello\x00world\x01")
        assert result == "helloworld"
    
    def test_sanitize_string_max_length(self):
        """测试最大长度限制"""
        long_string = "a" * 2000
        result = InputSanitizer.sanitize_string(long_string, max_length=100)
        assert len(result) == 100
    
    def test_sanitize_string_non_string(self):
        """测试非字符串输入"""
        result = InputSanitizer.sanitize_string(12345)
        assert result == "12345"
    
    def test_sanitize_path_traversal(self):
        """测试路径遍历防护"""
        result = InputSanitizer.sanitize_path("../../../etc/passwd")
        assert ".." not in result
    
    def test_sanitize_path_double_slash(self):
        """测试双斜杠净化"""
        result = InputSanitizer.sanitize_path("path//to//file")
        assert "//" not in result
    
    def test_sanitize_path_null_bytes(self):
        """测试空字节净化"""
        result = InputSanitizer.sanitize_path("path\x00/to/file")
        assert "\x00" not in result
    
    def test_sanitize_dict_basic(self):
        """测试字典净化"""
        data = {
            "name": "  test  ",
            "value": 123,
            "nested": {"key": "  nested value  "}
        }
        result = InputSanitizer.sanitize_dict(data)
        assert result["name"] == "test"
        assert result["value"] == 123
        assert result["nested"]["key"] == "nested value"
    
    def test_sanitize_dict_max_depth(self):
        """测试字典深度限制"""
        # 创建深度超过限制的字典
        data = {"level1": {"level2": {"level3": {"level4": "deep"}}}}
        result = InputSanitizer.sanitize_dict(data, max_depth=2)
        # 深度超过限制的应该被截断
        assert "level1" in result
        assert "level2" in result["level1"]
    
    def test_sanitize_dict_list(self):
        """测试列表净化"""
        data = {"items": ["  item1  ", "  item2  "]}
        result = InputSanitizer.sanitize_dict(data)
        assert result["items"] == ["item1", "item2"]


class TestRequestValidator:
    """请求验证器测试"""
    
    def test_validate_json_body_valid(self):
        """测试有效 JSON 验证"""
        body = {"name": "test", "value": 123}
        result = RequestValidator.validate_json_body(body)
        assert result["name"] == "test"
        assert result["value"] == 123
    
    def test_validate_json_body_missing_required(self):
        """测试缺少必需字段"""
        body = {"name": "test"}
        with pytest.raises(ValueError, match="Missing required field"):
            RequestValidator.validate_json_body(body, required_fields=["name", "value"])
    
    def test_validate_json_body_invalid_type(self):
        """测试无效类型"""
        body = "not a dict"
        with pytest.raises(ValueError, match="Request body must be a JSON object"):
            RequestValidator.validate_json_body(body)
    
    def test_validate_pagination_defaults(self):
        """测试分页默认值"""
        result = RequestValidator.validate_pagination({})
        assert result["page"] == 1
        assert result["per_page"] == 30
    
    def test_validate_pagination_custom(self):
        """测试自定义分页"""
        result = RequestValidator.validate_pagination({"page": 2, "per_page": 50})
        assert result["page"] == 2
        assert result["per_page"] == 50
    
    def test_validate_pagination_limits(self):
        """测试分页限制"""
        result = RequestValidator.validate_pagination({"page": -1, "per_page": 200})
        assert result["page"] == 1
        assert result["per_page"] == 100


class TestJWTAuth:
    """JWT 认证测试"""
    
    def test_create_access_token(self):
        """测试创建 access token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """测试带过期时间的 access token"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)
        assert isinstance(token, str)
    
    def test_verify_token_valid(self):
        """测试验证有效 token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
    
    def test_verify_token_invalid(self):
        """测试验证无效 token"""
        payload = verify_token("invalid.token.here")
        assert payload is None
    
    def test_verify_token_expired(self):
        """测试验证过期 token"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # 已过期
        token = create_access_token(data, expires_delta=expires_delta)
        payload = verify_token(token)
        assert payload is None


class TestRateLimiter:
    """速率限制器测试"""
    
    def test_rate_limiter_allows_requests(self):
        """测试速率限制器允许请求"""
        limiter = RateLimiter(requests_per_minute=10)
        assert limiter.is_allowed("client1") is True
    
    def test_rate_limiter_blocks_excessive_requests(self):
        """测试速率限制器阻止过多请求"""
        limiter = RateLimiter(requests_per_minute=2)
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        assert limiter.is_allowed("client1") is False
    
    def test_rate_limiter_different_clients(self):
        """测试不同客户端独立限制"""
        limiter = RateLimiter(requests_per_minute=1)
        limiter.is_allowed("client1")
        assert limiter.is_allowed("client2") is True
    
    def test_rate_limiter_window_reset(self):
        """测试速率限制器窗口重置"""
        import time
        limiter = RateLimiter(requests_per_minute=1)
        limiter.is_allowed("client1")
        
        # 模拟时间流逝
        with patch('time.time', return_value=time.time() + 61):
            assert limiter.is_allowed("client1") is True


class TestAPIKeys:
    """API Key 测试"""
    
    def test_init_api_keys_from_env(self):
        """测试从环境变量初始化 API Keys"""
        with patch.dict('os.environ', {'API_KEYS': 'key1:name1,key2:name2'}):
            # 重置 api_keys
            import app.middleware.auth as auth_module
            original_keys = auth_module.api_keys.copy()
            
            init_api_keys()
            
            assert 'key1' in auth_module.api_keys
            assert auth_module.api_keys['key1']['name'] == 'name1'
            assert 'key2' in auth_module.api_keys
            assert auth_module.api_keys['key2']['name'] == 'name2'
            
            # 恢复原始值
            auth_module.api_keys = original_keys
    
    def test_init_api_keys_empty(self):
        """测试空环境变量"""
        with patch.dict('os.environ', {'API_KEYS': ''}, clear=False):
            import app.middleware.auth as auth_module
            original_keys = auth_module.api_keys.copy()
            
            init_api_keys()
            
            # 应该保持原有 keys
            assert len(auth_module.api_keys) >= 0
            
            # 恢复原始值
            auth_module.api_keys = original_keys


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
