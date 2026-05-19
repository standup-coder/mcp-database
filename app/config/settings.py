"""
应用配置管理
使用Pydantic Settings进行类型安全的配置管理
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 高德地图配置
    amap_api_key: str = Field(..., env="AMAP_API_KEY")
    amap_origin: str = Field(..., env="AMAP_ORIGIN")  # 经度,纬度格式
    amap_destination: str = Field(..., env="AMAP_DESTINATION")  # 经度,纬度格式
    amap_strategy: int = Field(default=0, env="AMAP_STRATEGY")  # 0-速度优先, 1-费用优先, 2-距离优先
    
    # 钉钉配置
    dingtalk_webhook_url: str = Field(..., env="DINGTALK_WEBHOOK_URL")
    dingtalk_secret: str = Field(..., env="DINGTALK_SECRET")
    dingtalk_keyword: str = Field(default="通勤提醒", env="DINGTALK_KEYWORD")
    
    # Redis配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Celery配置
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    celery_accept_content: list = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    celery_timezone: str = Field(default="Asia/Shanghai", env="CELERY_TIMEZONE")
    celery_enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    
    # 定时任务配置
    commute_check_cron: str = Field(default="0 30 8 * * *", env="COMMUTE_CHECK_CRON")
    
    @property
    def redis_url(self) -> str:
        """构建Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app_env.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
