"""
错误处理和重试机制
提供统一的异常处理和自动重试功能
"""

import asyncio
import functools
import time
from typing import Callable, Any, Type, Tuple, Optional
from .logger import get_logger
from .exceptions import MCPBaseException

logger = get_logger(__name__)


class RetryConfig:
    """重试配置类"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.exceptions = exceptions


def retry(
    config: RetryConfig = None,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    重试装饰器
    
    Args:
        config: 重试配置对象
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 延迟倍数因子
        jitter: 是否添加随机抖动
        exceptions: 需要重试的异常类型元组
    """
    
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            delay=delay,
            backoff_factor=backoff_factor,
            jitter=jitter,
            exceptions=exceptions
        )
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts - 1:
                        # 最后一次尝试，直接抛出异常
                        logger.error(
                            f"函数 {func.__name__} 在第 {attempt + 1} 次尝试后仍然失败",
                            error=str(e),
                            function=func.__name__
                        )
                        raise
                    
                    # 计算延迟时间
                    delay_time = config.delay * (config.backoff_factor ** attempt)
                    if config.jitter:
                        import random
                        delay_time *= (0.5 + random.random() * 0.5)  # 0.5-1.0倍抖动
                    
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{delay_time:.2f}秒后重试",
                        error=str(e),
                        attempt=attempt + 1,
                        delay=delay_time,
                        function=func.__name__
                    )
                    
                    await asyncio.sleep(delay_time)
            
            # 这行代码理论上不会执行到
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"函数 {func.__name__} 在第 {attempt + 1} 次尝试后仍然失败",
                            error=str(e),
                            function=func.__name__
                        )
                        raise
                    
                    delay_time = config.delay * (config.backoff_factor ** attempt)
                    if config.jitter:
                        import random
                        delay_time *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{delay_time:.2f}秒后重试",
                        error=str(e),
                        attempt=attempt + 1,
                        delay=delay_time,
                        function=func.__name__
                    )
                    
                    time.sleep(delay_time)
            
            raise last_exception
        
        # 根据函数是否为异步函数选择合适的包装器
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def handle_exceptions(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    default_return: Any = None,
    log_level: str = "ERROR",
    reraise: bool = False
):
    """
    异常处理装饰器
    
    Args:
        exceptions: 要处理的异常类型元组
        default_return: 发生异常时的默认返回值
        log_level: 日志级别
        reraise: 是否重新抛出异常
    """
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                log_method = getattr(logger, log_level.lower(), logger.error)
                log_method(
                    f"函数 {func.__name__} 执行异常",
                    error=str(e),
                    function=func.__name__,
                    args=str(args)[:100],
                    kwargs=str(kwargs)[:100]
                )
                
                if reraise:
                    raise
                return default_return
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                log_method = getattr(logger, log_level.lower(), logger.error)
                log_method(
                    f"函数 {func.__name__} 执行异常",
                    error=str(e),
                    function=func.__name__,
                    args=str(args)[:100],
                    kwargs=str(kwargs)[:100]
                )
                
                if reraise:
                    raise
                return default_return
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class ErrorHandler:
    """错误处理器类"""
    
    @staticmethod
    def format_exception(exception: Exception) -> dict:
        """格式化异常信息"""
        return {
            "type": type(exception).__name__,
            "message": str(exception),
            "module": exception.__class__.__module__
        }
    
    @staticmethod
    def is_network_error(exception: Exception) -> bool:
        """判断是否为网络相关异常"""
        network_error_types = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )
        
        return isinstance(exception, network_error_types)
    
    @staticmethod
    def is_api_error(exception: Exception) -> bool:
        """判断是否为API相关异常"""
        return isinstance(exception, MCPBaseException)
    
    @staticmethod
    def get_retry_config_for_exception(exception: Exception) -> Optional[RetryConfig]:
        """根据异常类型返回相应的重试配置"""
        if ErrorHandler.is_network_error(exception):
            return RetryConfig(
                max_attempts=5,
                delay=2.0,
                backoff_factor=2.0,
                jitter=True,
                exceptions=(type(exception),)
            )
        elif ErrorHandler.is_api_error(exception):
            return RetryConfig(
                max_attempts=3,
                delay=1.0,
                backoff_factor=1.5,
                jitter=True,
                exceptions=(type(exception),)
            )
        else:
            return None


# 预定义的重试配置
NETWORK_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    delay=2.0,
    backoff_factor=2.0,
    jitter=True,
    exceptions=(ConnectionError, TimeoutError, asyncio.TimeoutError)
)

API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    delay=1.0,
    backoff_factor=1.5,
    jitter=True,
    exceptions=(MCPBaseException,)
)

DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    delay=1.0,
    backoff_factor=2.0,
    jitter=True
)