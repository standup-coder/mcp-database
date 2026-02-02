"""
日志上下文管理器
用于在特定操作范围内添加额外的日志上下文信息
"""

from contextlib import contextmanager
from typing import Dict, Any
from .logger import get_logger


@contextmanager
def log_context(**kwargs):
    """
    日志上下文管理器，在指定代码块中添加额外的日志信息
    
    Args:
        **kwargs: 要添加到日志中的键值对
        
    Usage:
        with log_context(task_id="12345", user_id="user_001"):
            # 这里的所有日志都会包含 task_id 和 user_id 信息
            logger.info("开始处理任务")
    """
    logger = get_logger()
    
    # 添加上下文信息到日志记录器
    bound_logger = logger.bind(**kwargs)
    
    try:
        yield bound_logger
    finally:
        # 上下文结束时自动清理
        pass


class LogContext:
    """
    日志上下文装饰器类
    可以作为装饰器或上下文管理器使用
    """
    
    def __init__(self, **context_data: Dict[str, Any]):
        self.context_data = context_data
        self.logger = get_logger()
    
    def __enter__(self):
        """上下文管理器进入"""
        self.bound_logger = self.logger.bind(**self.context_data)
        return self.bound_logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if exc_type:
            # 如果有异常，记录错误信息
            self.bound_logger.error(
                "上下文执行异常",
                exception=str(exc_val),
                exc_type=str(exc_type.__name__)
            )
        return False  # 不抑制异常
    
    def __call__(self, func):
        """装饰器用法"""
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper


def task_log_context(task_name: str):
    """
    任务日志上下文装饰器
    
    Args:
        task_name: 任务名称
        
    Usage:
        @task_log_context("route_calculation")
        def calculate_route():
            logger.info("开始计算路线")
    """
    import uuid
    from datetime import datetime
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            task_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            context_data = {
                "task_id": task_id,
                "task_name": task_name,
                "start_time": timestamp
            }
            
            with LogContext(**context_data) as logger:
                logger.info(f"开始执行任务: {task_name}")
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"任务执行成功: {task_name}")
                    return result
                except Exception as e:
                    logger.error(f"任务执行失败: {task_name}", error=str(e))
                    raise
        return wrapper
    return decorator


# 便捷函数
def route_calculation_context():
    """路线计算任务的日志上下文"""
    return task_log_context("route_calculation")


def message_send_context():
    """消息发送任务的日志上下文"""
    return task_log_context("message_send")


def commute_check_context():
    """通勤检查任务的日志上下文"""
    return task_log_context("commute_check")