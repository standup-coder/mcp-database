"""
应用主入口文件
FastAPI应用配置和路由定义
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any

from .config.settings import settings
from .utils.logger import get_logger, setup_logger
from .services.commute_service import CommuteService
from .workers.tasks import check_commute_and_notify, health_check

# 初始化日志系统
setup_logger()

logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="MCP Commute Assistant API",
    description="智能通勤助手API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("MCP Commute Assistant API服务启动")
    logger.info(f"运行环境: {settings.app_env}")
    logger.info(f"调试模式: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("MCP Commute Assistant API服务关闭")


@app.get("/")
async def root() -> Dict[str, Any]:
    """根路径"""
    return {
        "message": "欢迎使用MCP智能通勤助手API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check_endpoint() -> Dict[str, Any]:
    """健康检查端点"""
    try:
        service = CommuteService()
        result = await service.health_check()
        return result
    except Exception as e:
        logger.error("健康检查端点异常", error=str(e))
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@app.post("/commute/check")
async def check_commute() -> Dict[str, Any]:
    """手动触发通勤检查"""
    try:
        logger.info("收到手动通勤检查请求")
        
        # 异步执行任务
        task = check_commute_and_notify.delay()
        
        return {
            "message": "通勤检查任务已启动",
            "task_id": task.id,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("通勤检查请求处理失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"任务启动失败: {str(e)}")


@app.get("/commute/status/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """获取任务状态"""
    try:
        from celery.result import AsyncResult
        
        task = AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("获取任务状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@app.get("/config/info")
async def get_config_info() -> Dict[str, Any]:
    """获取配置信息（仅开发环境）"""
    if not settings.is_development:
        raise HTTPException(status_code=403, detail="此接口仅在开发环境可用")
    
    masked_config = {
        "app_env": settings.app_env,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "amap_origin": settings.amap_origin,
        "amap_destination": settings.amap_destination,
        "amap_strategy": settings.amap_strategy,
        "dingtalk_keyword": settings.dingtalk_keyword,
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "celery_timezone": settings.celery_timezone,
        "commute_check_cron": settings.commute_check_cron
    }
    
    return {
        "config": masked_config,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/test/notification")
async def test_notification() -> Dict[str, Any]:
    """测试通知发送（仅开发环境）"""
    if not settings.is_development:
        raise HTTPException(status_code=403, detail="此接口仅在开发环境可用")
    
    try:
        from .mcp.dingtalk_client import send_simple_message
        import asyncio
        
        result = await send_simple_message("🔧 测试消息 - 系统运行正常")
        
        return {
            "message": "测试通知发送成功",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("测试通知发送失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"测试通知发送失败: {str(e)}")


# 异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(
        "未处理的异常",
        error=str(exc),
        request_url=str(request.url),
        request_method=request.method
    )
    
    return {
        "error": "内部服务器错误",
        "detail": str(exc) if settings.debug else "请查看日志获取详细信息",
        "timestamp": datetime.now().isoformat()
    }


def create_app() -> FastAPI:
    """创建应用实例"""
    return app


if __name__ == "__main__":
    # 直接运行时的配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )