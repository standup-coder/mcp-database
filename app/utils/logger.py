"""
日志系统配置
使用Loguru实现结构化日志记录
"""

import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
from ..config.settings import settings


def setup_logger():
    """配置日志系统"""
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出配置
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.log_level,
        colorize=True,
        enqueue=True  # 异步写入
    )
    
    # 文件输出配置
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 详细日志文件
    detailed_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message} | "
        "{extra}"
    )
    
    logger.add(
        logs_dir / "mcp_commute_{time:YYYY-MM-DD}.log",
        format=detailed_format,
        level="DEBUG",
        rotation="00:00",  # 每天轮转
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
        enqueue=True,
        serialize=False
    )
    
    # 错误日志文件
    logger.add(
        logs_dir / "error_{time:YYYY-MM-DD}.log",
        format=detailed_format,
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        enqueue=True,
        serialize=False
    )
    
    # 结构化JSON日志（用于分析）
    logger.add(
        logs_dir / "structured_{time:YYYY-MM-DD}.json",
        format="{message}",
        level="INFO",
        rotation="00:00",
        retention="7 days",
        compression="zip",
        enqueue=True,
        serialize=True  # JSON序列化
    )
    
    logger.info("日志系统初始化完成")
    logger.info(f"日志级别: {settings.log_level}")
    logger.info(f"日志目录: {logs_dir.absolute()}")
    
    return logger


def get_logger(name: str = None):
    """获取日志记录器实例"""
    if name:
        return logger.bind(name=name)
    return logger


# 初始化全局日志记录器
app_logger = setup_logger()

# 导出常用方法
debug = app_logger.debug
info = app_logger.info
warning = app_logger.warning
error = app_logger.error
critical = app_logger.critical
exception = app_logger.exception