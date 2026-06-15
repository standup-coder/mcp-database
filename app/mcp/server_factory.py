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
    FILESYSTEM = "filesystem"
    GIT = "git"
    DATABASE = "database"
    HTTP = "http"
    SLACK = "slack"
    GITHUB = "github"
    BRAVE_SEARCH = "brave_search"
    NOTION = "notion"
    GOOGLE_SHEETS = "google_sheets"
    BROWSER = "browser"
    MEMORY = "memory"
    CONTEXT7 = "context7"
    SEQUENTIAL_THINKING = "sequential_thinking"
    DESKTOP_COMMANDER = "desktop_commander"
    DOCFORK = "docfork"
    DEEPWIKI = "deepwiki"
    FIGMA = "figma"
    REACTBITS = "reactbits"
    E2B = "e2b"
    SENTRY = "sentry"
    LINEAR = "linear"
    COMPOSIO = "composio"


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
            ),
            ServerType.FILESYSTEM: ManagedServer(
                name="filesystem-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.filesystem_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.GIT: ManagedServer(
                name="git-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.git_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.DATABASE: ManagedServer(
                name="database-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.database_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.HTTP: ManagedServer(
                name="http-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.http_client_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=30,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.SLACK: ManagedServer(
                name="slack-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.slack_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.GITHUB: ManagedServer(
                name="github-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.github_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.BRAVE_SEARCH: ManagedServer(
                name="brave-search-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.brave_search_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.NOTION: ManagedServer(
                name="notion-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.notion_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.GOOGLE_SHEETS: ManagedServer(
                name="google-sheets-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.google_sheets_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.BROWSER: ManagedServer(
                name="browser-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.browser_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=5,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.MEMORY: ManagedServer(
                name="memory-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.memory_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.CONTEXT7: ManagedServer(
                name="context7-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.context7_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.SEQUENTIAL_THINKING: ManagedServer(
                name="sequential-thinking-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.sequential_thinking_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.DESKTOP_COMMANDER: ManagedServer(
                name="desktop-commander-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.desktop_commander_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.DOCFORK: ManagedServer(
                name="docfork-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.docfork_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.DEEPWIKI: ManagedServer(
                name="deepwiki-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.deepwiki_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.FIGMA: ManagedServer(
                name="figma-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.figma_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.REACTBITS: ManagedServer(
                name="reactbits-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.reactbits_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=20,
                auto_restart=True,
                health_check_interval=120
            ),
            ServerType.E2B: ManagedServer(
                name="e2b-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.e2b_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=10,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.SENTRY: ManagedServer(
                name="sentry-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.sentry_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.LINEAR: ManagedServer(
                name="linear-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.linear_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=60
            ),
            ServerType.COMPOSIO: ManagedServer(
                name="composio-mcp-server",
                command="python",
                args=["-m", "app.mcp.servers.composio_server"],
                env={"PYTHONPATH": "."},
                working_dir=".",
                timeout=300,
                max_concurrent=15,
                auto_restart=True,
                health_check_interval=60
            ),
        }
        
        for key, value in builtin_configs.items():
            self.registered_configs[key.value] = value
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
        special_paths = {
            ServerType.HTTP: "app.mcp.servers.http_client_server",
            ServerType.BRAVE_SEARCH: "app.mcp.servers.brave_search_server",
            ServerType.GOOGLE_SHEETS: "app.mcp.servers.google_sheets_server",
        }
        if server_type in special_paths:
            return special_paths[server_type]
        return f"app.mcp.servers.{server_type.value}_server"
    
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