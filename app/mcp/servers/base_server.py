"""
MCP服务器基础模板
所有MCP服务器都应继承此基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ServerCapability(Enum):
    """MCP服务器能力枚举"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    STREAM = "stream"
    TRANSFORM = "transform"


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    capability: ServerCapability = ServerCapability.READ


@dataclass
class MCPResource:
    """MCP资源定义"""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"


class BaseMCPServer(ABC):
    """MCP服务器基类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self._tools: Dict[str, MCPTool] = {}
        self._resources: Dict[str, MCPResource] = {}
        self._initialize()
    
    def _initialize(self):
        """初始化服务器，注册工具和资源"""
        self.register_tools()
        self.register_resources()
    
    @abstractmethod
    def register_tools(self):
        """注册MCP工具，子类必须实现"""
        pass
    
    @abstractmethod
    def register_resources(self):
        """注册MCP资源，子类必须实现"""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行工具，子类必须实现"""
        pass
    
    def get_tools(self) -> List[MCPTool]:
        """获取所有工具"""
        return list(self._tools.values())
    
    def get_resources(self) -> List[MCPResource]:
        """获取所有资源"""
        return list(self._resources.values())
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """获取指定工具"""
        return self._tools.get(name)
    
    def get_resource(self, uri: str) -> Optional[MCPResource]:
        """获取指定资源"""
        return self._resources.get(uri)
    
    def _register_tool(self, tool: MCPTool):
        """注册工具"""
        self._tools[tool.name] = tool
    
    def _register_resource(self, resource: MCPResource):
        """注册资源"""
        self._resources[resource.uri] = resource
    
    async def handle_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """处理MCP请求"""
        params = params or {}
        
        if method == "tools/list":
            return {"tools": [t.__dict__ for t in self.get_tools()]}
        elif method == "resources/list":
            return {"resources": [r.__dict__ for r in self.get_resources()]}
        elif method.startswith("tools/"):
            tool_name = method.replace("tools/", "")
            return await self.execute_tool(tool_name, params)
        elif method.startswith("resources/"):
            resource_uri = method.replace("resources/", "")
            return await self.read_resource(resource_uri)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def read_resource(self, uri: str) -> Any:
        """读取资源"""
        resource = self.get_resource(uri)
        if not resource:
            raise ValueError(f"Resource not found: {uri}")
        return await self._read_resource_content(resource)
    
    @abstractmethod
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容，子类必须实现"""
        pass
