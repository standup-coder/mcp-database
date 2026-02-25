"""
Brave Search MCP服务器
提供网页搜索功能
"""

import os
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class BraveSearchMCPServer(BaseMCPServer):
    """Brave Search MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.api_key = config.get("api_key", os.environ.get("BRAVE_API_KEY", ""))
        super().__init__(config)
    
    def register_tools(self):
        """注册搜索工具"""
        self._register_tool(MCPTool(
            name="search",
            description="网页搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "搜索查询"},
                    "count": {"type": "integer", "default": 10},
                    "offset": {"type": "integer", "default": 0}
                },
                "required": ["q"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="news",
            description="新闻搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "搜索查询"},
                    "count": {"type": "integer", "default": 10}
                },
                "required": ["q"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="images",
            description="图片搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "搜索查询"},
                    "count": {"type": "integer", "default": 10}
                },
                "required": ["q"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="videos",
            description="视频搜索",
            input_schema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "搜索查询"},
                    "count": {"type": "integer", "default": 10}
                },
                "required": ["q"]
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册资源"""
        self._register_resource(MCPResource(
            uri="brave://last_search",
            name="last_search_results",
            description="上次搜索结果"
        ))
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行搜索"""
        import httpx
        
        q = params.get("q", "")
        count = params.get("count", 10)
        
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        } if self.api_key else {}
        
        base_url = "https://api.search.brave.com/res/v1"
        
        async with httpx.AsyncClient() as client:
            if tool_name == "search":
                url = f"{base_url}/web/search"
                params = {"q": q, "count": count}
                response = await client.get(url, headers=headers, params=params)
            
            elif tool_name == "news":
                url = f"{base_url}/news/search"
                params = {"q": q, "count": count}
                response = await client.get(url, headers=headers, params=params)
            
            elif tool_name == "images":
                url = f"{base_url}/images/search"
                params = {"q": q, "count": count}
                response = await client.get(url, headers=headers, params=params)
            
            elif tool_name == "videos":
                url = f"{base_url}/videos/search"
                params = {"q": q, "count": count}
                response = await client.get(url, headers=headers, params=params)
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            if response.status_code >= 400:
                return {"error": f"API error: {response.status_code}", "detail": response.text}
            
            return response.json()
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "brave://last_search":
            return "No search performed yet"
        raise ValueError(f"Unknown resource: {resource.uri}")
