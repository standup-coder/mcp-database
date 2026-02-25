"""
HTTP客户端MCP服务器
提供HTTP请求功能
"""

import httpx
from typing import Any, Dict, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class HTTPClientMCPServer(BaseMCPServer):
    """HTTP客户端MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.default_timeout = config.get("timeout", 30) if config else 30
        self.default_headers = config.get("headers", {}) if config else {}
        super().__init__(config)
    
    def register_tools(self):
        """注册HTTP操作工具"""
        self._register_tool(MCPTool(
            name="get",
            description="发送GET请求",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "请求URL"},
                    "params": {"type": "object", "description": "查询参数"},
                    "headers": {"type": "object", "description": "请求头"}
                },
                "required": ["url"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="post",
            description="发送POST请求",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "请求URL"},
                    "data": {"type": "object", "description": "请求数据"},
                    "json": {"type": "object", "description": "JSON数据"},
                    "headers": {"type": "object", "description": "请求头"}
                },
                "required": ["url"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="put",
            description="发送PUT请求",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "请求URL"},
                    "data": {"type": "object", "description": "请求数据"},
                    "json": {"type": "object", "description": "JSON数据"},
                    "headers": {"type": "object", "description": "请求头"}
                },
                "required": ["url"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="delete",
            description="发送DELETE请求",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "请求URL"},
                    "headers": {"type": "object", "description": "请求头"}
                },
                "required": ["url"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="request",
            description="发送自定义HTTP请求",
            input_schema={
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP方法"},
                    "url": {"type": "string", "description": "请求URL"},
                    "params": {"type": "object", "description": "查询参数"},
                    "data": {"type": "object", "description": "表单数据"},
                    "json": {"type": "object", "description": "JSON数据"},
                    "headers": {"type": "object", "description": "请求头"},
                    "timeout": {"type": "integer", "description": "超时时间"}
                },
                "required": ["method", "url"]
            },
            capability=ServerCapability.EXECUTE
        ))
    
    def register_resources(self):
        """注册HTTP资源"""
        self._register_resource(MCPResource(
            uri="http://last_response",
            name="last_response",
            description="上次请求的响应"
        ))
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行HTTP请求"""
        method = params.get("method", tool_name.upper())
        url = params.get("url", "")
        headers = {**self.default_headers, **(params.get("headers", {}))}
        timeout = params.get("timeout", self.default_timeout)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            if tool_name in ("get", "post", "put", "delete"):
                method = tool_name.upper()
            
            request_params = {
                "url": url,
                "headers": headers,
            }
            
            if method in ("POST", "PUT", "PATCH"):
                if "json" in params:
                    request_params["json"] = params["json"]
                elif "data" in params:
                    request_params["data"] = params["data"]
            
            if "params" in params:
                request_params["params"] = params["params"]
            
            response = await client.request(method, **request_params)
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "json": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            }
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "http://last_response":
            return "No response yet"
        raise ValueError(f"Unknown resource: {resource.uri}")
