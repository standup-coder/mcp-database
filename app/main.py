"""
应用主入口文件
FastAPI应用配置和路由定义
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .config.settings import settings
from .utils.logger import get_logger, setup_logger
from .services.commute_service import CommuteService
from .workers.tasks import check_commute_and_notify, health_check
from .mcp.server_factory import server_factory, ServerType
from .middleware.auth import require_auth, optional_auth, check_rate_limit, create_access_token
from .middleware.security import SecurityHeadersMiddleware, InputSanitizer, RequestValidator

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
# 安全改进：限制允许的来源，不再使用 *
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

# 在生产环境中，从环境变量加载允许的来源
if settings.is_production:
    import os
    allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
    if allowed_origins_env:
        ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# 添加安全头中间件
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=settings.is_production,  # 仅在生产环境启用 HSTS
    enable_csp=True,
    enable_xss_protection=True,
    enable_content_type_options=True,
    enable_frame_options=True,
    enable_referrer_policy=True,
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
        "message": "欢迎使用MCP工具大全API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# MCP服务器管理端点
@app.get("/mcp/servers")
async def list_mcp_servers() -> Dict[str, Any]:
    """列出所有可用的MCP服务器"""
    servers = server_factory.list_available_servers()
    return {
        "servers": [
            {
                "name": name,
                "config": {
                    "command": config.command,
                    "args": config.args,
                    "timeout": config.timeout,
                    "max_concurrent": config.max_concurrent,
                    "auto_restart": config.auto_restart
                }
            }
            for name, config in servers.items()
        ],
        "total": len(servers),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/mcp/servers/{server_name}")
async def get_mcp_server_info(server_name: str) -> Dict[str, Any]:
    """获取指定MCP服务器信息"""
    config = server_factory.get_server_config(server_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"服务器不存在: {server_name}")
    
    return {
        "name": config.name,
        "command": config.command,
        "args": config.args,
        "env": config.env,
        "working_dir": config.working_dir,
        "timeout": config.timeout,
        "max_concurrent": config.max_concurrent,
        "auto_restart": config.auto_restart,
        "health_check_interval": config.health_check_interval,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/mcp/server-types")
async def list_server_types() -> Dict[str, Any]:
    """列出所有可用的服务器类型"""
    return {
        "server_types": [
            {"value": t.value, "name": t.name}
            for t in ServerType
        ],
        "timestamp": datetime.now().isoformat()
    }


@app.post("/mcp/execute/{server_name}/{tool_name}")
async def execute_mcp_tool(
    server_name: str,
    tool_name: str,
    params: Optional[Dict[str, Any]] = None,
    auth: Dict[str, Any] = Depends(require_auth)  # 要求认证
) -> Dict[str, Any]:
    """执行MCP服务器工具"""
    if params is None:
        params = {}
    
    try:
        # 验证和净化输入
        params = InputSanitizer.sanitize_dict(params)
        
        server_config = server_factory.get_server_config(server_name)
        if not server_config:
            raise HTTPException(status_code=404, detail=f"服务器不存在: {server_name}")
        
        # 安全改进：使用 importlib 替代 __import__
        import importlib
        module_path = f"app.mcp.servers.{server_name}_server"
        module = importlib.import_module(module_path)
        server_class_name = f"{server_name.upper()}MCPServer"
        server_class = getattr(module, server_class_name, None)
        
        if not server_class:
            raise HTTPException(status_code=404, detail=f"未找到服务器类: {server_class_name}")
        
        server = server_class(config={})
        result = await server.execute_tool(tool_name, params)
        
        return {
            "server": server_name,
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP工具执行失败: {server_name}/{tool_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"工具执行失败: {str(e)}")


@app.post("/auth/token")
async def create_token(username: str, password: str) -> Dict[str, Any]:
    """创建 JWT token（示例端点 - 生产环境应连接到用户数据库）"""
    import os
    if settings.is_production:
        raise HTTPException(
            status_code=403,
            detail="Demo token endpoint is disabled in production. Use your own auth provider."
        )
    demo_username = os.environ.get("DEMO_USERNAME", "demo")
    demo_password = os.environ.get("DEMO_PASSWORD", "demo")
    if username == demo_username and password == demo_password:
        access_token = create_access_token(data={"sub": username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/auth/me")
async def get_current_user_info(auth: Dict[str, Any] = Depends(optional_auth)) -> Dict[str, Any]:
    """获取当前认证用户信息"""
    if auth is None:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": auth}


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


@app.get("/ui")
async def get_ui():
    """MCP管理界面"""
    import os
    web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "mcp_manager.html")
    return FileResponse(web_path)


if __name__ == "__main__":
    # 直接运行时的配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )