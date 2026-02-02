"""
MCP服务器工厂
负责创建和管理各种类型的MCP服务器实例
"""

import importlib
from typing import Dict, Type, Any, Optional
from enum import Enum

from ..utils.logger import get_logger
from .server_manager import ManagedServer

logger = get_logger(__name__)


class ServerType(Enum):
    """服务器类型枚举"""
    AMAP = "amap"
    DINGTALK = "dingtalk"
    WEATHER = "weather"
    CALENDAR = "calendar"
    CUSTOM = "custom"
    NEWS = "news"
    STOCK = "stock"
    TRANSLATION = "translation"


class ServerFactory:
    """MCP服务器工厂"""
    
    def __init__(self):
        self.server_classes: Dict[ServerType, Type] = {}
        self.registered_configs: Dict[str, ManagedServer] = {}
        self._load_builtin_servers()
    
    def _load_builtin_servers(self):
        """加载内置服务器配置"""
        builtin_configs = {
            ServerType.AMAP: ManagedServer(
                name="amap-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.amap_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=5,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.DINGTALK: ManagedServer(
                name="dingtalk-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.dingtalk_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.WEATHER: ManagedServer(
                name="weather-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.weather_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.CALENDAR: ManagedServer(
                name="calendar-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.calendar_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=120
            )
        }
        
        self.registered_configs.update(builtin_configs)
        logger.info("内置MCP服务器配置加载完成")
    
    def register_custom_server(
        self,
        name: str,
        server_type: ServerType,
        config: ManagedServer
    ) -> bool:
        """注册自定义服务器"""
        try:
            self.registered_configs[name] = config
            logger.info(f"自定义服务器注册成功: {name}")
            return True
        except Exception as e:
            logger.error(f"自定义服务器注册失败: {name}", error=str(e))
            return False
    
    def get_server_config(self, name: str) -> Optional[ManagedServer]:
        """获取服务器配置"""
        return self.registered_configs.get(name)
    
    def list_available_servers(self) -> Dict[str, ManagedServer]:
        """列出所有可用的服务器配置"""
        return self.registered_configs.copy()
    
    def create_server_instance(
        self,
        server_name: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Optional[ManagedServer]:
        """创建服务器实例配置"""
        base_config = self.get_server_config(server_name)
        if not base_config:
            logger.error(f"服务器配置不存在: {server_name}")
            return None
        
        # 如果有自定义配置，合并配置
        if custom_config:
            config_dict = base_config.dict()
            config_dict.update(custom_config)
            try:
                return ManagedServer(**config_dict)
            except Exception as e:
                logger.error(f"服务器配置合并失败: {server_name}", error=str(e))
                return None
        
        return base_config
    
    def get_server_module_path(self, server_type: ServerType) -> str:
        """获取服务器模块路径"""
        module_paths = {
            ServerType.AMAP: "app.mcp.servers.amap_server",
            ServerType.DINGTALK: "app.mcp.servers.dingtalk_server",
            ServerType.WEATHER: "app.mcp.servers.weather_server",
            ServerType.CALENDAR: "app.mcp.servers.calendar_server",
        }
        return module_paths.get(server_type, "")
    
    async def load_server_class(self, server_type: ServerType) -> Optional[Type]:
        """动态加载服务器类"""
        if server_type in self.server_classes:
            return self.server_classes[server_type]
        
        try:
            module_path = self.get_server_module_path(server_type)
            if not module_path:
                return None
            
            module = importlib.import_module(module_path)
            server_class = getattr(module, f"{server_type.value.upper()}MCPServer", None)
            
            if server_class:
                self.server_classes[server_type] = server_class
                logger.debug(f"服务器类加载成功: {server_type.value}")
                return server_class
            else:
                logger.warning(f"未找到服务器类: {server_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"服务器类加载失败: {server_type.value}", error=str(e))
            return None
    
    def validate_server_config(self, config: ManagedServer) -> bool:
        """验证服务器配置"""
        try:
            # 基本验证
            if not config.name:
                raise ValueError("服务器名称不能为空")
            
            if not config.command:
                raise ValueError("服务器命令不能为空")
            
            # 检查命令是否存在（简单检查）
            import shutil
            if not shutil.which(config.command):
                logger.warning(f"命令可能不存在: {config.command}")
            
            # 参数验证
            if config.timeout <= 0:
                raise ValueError("超时时间必须大于0")
            
            if config.max_concurrent <= 0:
                raise ValueError("最大并发数必须大于0")
            
            if config.health_check_interval <= 0:
                raise ValueError("健康检查间隔必须大于0")
            
            return True
            
        except Exception as e:
            logger.error(f"服务器配置验证失败: {config.name}", error=str(e))
            return False


# 全局服务器工厂实例
server_factory = ServerFactory()