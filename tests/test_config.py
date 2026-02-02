"""
配置模块测试
"""

import os
import pytest
from unittest.mock import patch
from app.config.settings import Settings
from app.config.validators import (
    validate_coordinates,
    validate_amap_api_key,
    validate_dingtalk_webhook,
    validate_cron_expression,
    validate_all_config
)
from app.utils.exceptions import ConfigValidationError


class TestSettings:
    """配置设置测试类"""
    
    def test_settings_defaults(self):
        """测试默认配置值"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.app_env == "development"
            assert settings.debug is False
            assert settings.log_level == "INFO"
            assert settings.redis_host == "localhost"
            assert settings.redis_port == 6379
    
    def test_settings_from_env(self):
        """测试从环境变量加载配置"""
        env_vars = {
            "APP_ENV": "production",
            "DEBUG": "True",
            "LOG_LEVEL": "DEBUG",
            "AMAP_API_KEY": "test_key_123",
            "AMAP_ORIGIN": "116.481485,39.990464",
            "AMAP_DESTINATION": "116.481485,39.990464",
            "DINGTALK_WEBHOOK_URL": "https://oapi.dingtalk.com/robot/send?access_token=test",
            "DINGTALK_SECRET": "test_secret",
            "CELERY_BROKER_URL": "redis://localhost:6379/1",
            "CELERY_RESULT_BACKEND": "redis://localhost:6379/2"
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.app_env == "production"
            assert settings.debug is True
            assert settings.log_level == "DEBUG"
            assert settings.amap_api_key == "test_key_123"
    
    def test_redis_url_property(self):
        """测试Redis URL属性"""
        # 无密码情况
        settings = Settings(REDIS_HOST="localhost", REDIS_PORT=6379, REDIS_DB=0)
        assert settings.redis_url == "redis://localhost:6379/0"
        
        # 有密码情况
        settings = Settings(
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DB=0,
            REDIS_PASSWORD="password123"
        )
        assert settings.redis_url == "redis://:password123@localhost:6379/0"
    
    def test_environment_properties(self):
        """测试环境判断属性"""
        settings_dev = Settings(APP_ENV="development")
        settings_prod = Settings(APP_ENV="production")
        
        assert settings_dev.is_development is True
        assert settings_dev.is_production is False
        assert settings_prod.is_development is False
        assert settings_prod.is_production is True


class TestValidators:
    """配置验证器测试类"""
    
    def test_validate_coordinates_valid(self):
        """测试有效坐标验证"""
        # 正常坐标
        lon, lat = validate_coordinates("116.481485,39.990464")
        assert abs(lon - 116.481485) < 0.000001
        assert abs(lat - 39.990464) < 0.000001
        
        # 边界值
        lon, lat = validate_coordinates("180,90")
        assert lon == 180
        assert lat == 90
    
    def test_validate_coordinates_invalid(self):
        """测试无效坐标验证"""
        # 空字符串
        with pytest.raises(ConfigValidationError, match="坐标不能为空"):
            validate_coordinates("")
        
        # 格式错误
        with pytest.raises(ConfigValidationError, match="坐标格式错误"):
            validate_coordinates("116.481485")
        
        with pytest.raises(ConfigValidationError, match="坐标格式错误"):
            validate_coordinates("116.481485,39.990464,extra")
        
        # 超出范围
        with pytest.raises(ConfigValidationError, match="经度超出范围"):
            validate_coordinates("181,39.990464")
        
        with pytest.raises(ConfigValidationError, match="纬度超出范围"):
            validate_coordinates("116.481485,91")
        
        # 无效数值
        with pytest.raises(ConfigValidationError, match="坐标值无效"):
            validate_coordinates("not_a_number,39.990464")
    
    def test_validate_amap_api_key(self):
        """测试高德API Key验证"""
        # 有效Key
        assert validate_amap_api_key("test_key_123") is True
        assert validate_amap_api_key("abcdefghijklmnopqrstuvwxyz") is True
        
        # 无效Key
        assert validate_amap_api_key("") is False
        assert validate_amap_api_key("ab") is False  # 太短
        assert validate_amap_api_key(None) is False
    
    def test_validate_dingtalk_webhook(self):
        """测试钉钉Webhook URL验证"""
        # 有效URL
        assert validate_dingtalk_webhook("https://oapi.dingtalk.com/robot/send?access_token=test") is True
        assert validate_dingtalk_webhook("http://dingtalk.com/test") is True
        
        # 无效URL
        assert validate_dingtalk_webhook("") is False
        assert validate_dingtalk_webhook(None) is False
        assert validate_dingtalk_webhook("invalid_url") is False
        assert validate_dingtalk_webhook("https://example.com/test") is False  # 不是钉钉域名
    
    def test_validate_cron_expression(self):
        """测试Cron表达式验证"""
        # 有效表达式
        assert validate_cron_expression("0 30 8 * * *") is True
        assert validate_cron_expression("* * * * * *") is True
        
        # 无效表达式
        assert validate_cron_expression("") is False
        assert validate_cron_expression("0 30 8 * *") is False  # 缺少字段
        assert validate_cron_expression("0 30 8 * * * extra") is False  # 多余字段
        assert validate_cron_expression(None) is False
    
    def test_validate_all_config(self):
        """测试完整配置验证"""
        valid_config = {
            'AMAP_API_KEY': 'test_key_123',
            'AMAP_ORIGIN': '116.481485,39.990464',
            'AMAP_DESTINATION': '116.481485,39.990464',
            'DINGTALK_WEBHOOK_URL': 'https://oapi.dingtalk.com/robot/send?access_token=test',
            'DINGTALK_SECRET': 'test_secret',
            'COMMUTE_CHECK_CRON': '0 30 8 * * *'
        }
        
        # 有效配置
        result = validate_all_config(valid_config)
        assert result == valid_config
        
        # 缺少必需字段
        invalid_config = valid_config.copy()
        del invalid_config['AMAP_API_KEY']
        
        with pytest.raises(ConfigValidationError, match="缺少必需配置项: AMAP_API_KEY"):
            validate_all_config(invalid_config)
        
        # 坐标格式错误
        invalid_config = valid_config.copy()
        invalid_config['AMAP_ORIGIN'] = 'invalid_coordinate'
        
        with pytest.raises(ConfigValidationError, match="出发地坐标错误"):
            validate_all_config(invalid_config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])