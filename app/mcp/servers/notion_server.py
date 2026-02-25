"""
Notion MCP服务器
提供Notion API操作功能
"""

import os
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class NotionMCPServer(BaseMCPServer):
    """Notion MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.token = config.get("token", os.environ.get("NOTION_TOKEN", ""))
        super().__init__(config)
    
    def register_tools(self):
        """注册Notion操作工具"""
        self._register_tool(MCPTool(
            name="search",
            description="搜索Notion页面",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "filter": {"type": "object", "description": "过滤条件"},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_page",
            description="获取页面内容",
            input_schema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "页面ID"}
                },
                "required": ["page_id"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="create_page",
            description="创建新页面",
            input_schema={
                "type": "object",
                "properties": {
                    "parent_page_id": {"type": "string", "description": "父页面ID"},
                    "title": {"type": "string", "description": "页面标题"},
                    "content": {"type": "string", "description": "页面内容"}
                },
                "required": ["title"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="create_database",
            description="创建数据库",
            input_schema={
                "type": "object",
                "properties": {
                    "parent_page_id": {"type": "string", "description": "父页面ID"},
                    "title": {"type": "string", "description": "数据库标题"},
                    "properties": {"type": "object", "description": "数据库属性"}
                },
                "required": ["title"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="query_database",
            description="查询数据库",
            input_schema={
                "type": "object",
                "properties": {
                    "database_id": {"type": "string", "description": "数据库ID"},
                    "filter": {"type": "object", "description": "过滤条件"},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["database_id"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="append_block_children",
            description="添加块内容",
            input_schema={
                "type": "object",
                "properties": {
                    "block_id": {"type": "string", "description": "块ID"},
                    "content": {"type": "string", "description": "文本内容"}
                },
                "required": ["block_id", "content"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="list_databases",
            description="列出所有数据库",
            input_schema={
                "type": "object",
                "properties": {
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册资源"""
        self._register_resource(MCPResource(
            uri="notion://databases",
            name="database_list",
            description="数据库列表"
        ))
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """发送Notion API请求"""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        url = f"https://api.notion.com/v1{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code >= 400:
                raise ValueError(f"Notion API error: {response.text}")
            
            return response.json()
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行Notion操作"""
        page_id = params.get("page_id", "")
        database_id = params.get("database_id", "")
        
        if tool_name == "search":
            return await self._make_request("POST", "/search", {
                "query": params.get("query", ""),
                "page_size": params.get("page_size", 10)
            })
        
        elif tool_name == "get_page":
            return await self._make_request("GET", f"/pages/{page_id}")
        
        elif tool_name == "create_page":
            data = {
                "parent": {"page_id": params.get("parent_page_id", "")},
                "properties": {
                    "title": {
                        "title": [{"text": {"content": params.get("title", "")}}]
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": params.get("content", "")}}]
                        }
                    }
                ]
            }
            return await self._make_request("POST", "/pages", data)
        
        elif tool_name == "create_database":
            data = {
                "parent": {"page_id": params.get("parent_page_id", "")},
                "title": [{"text": {"content": params.get("title", "")}}],
                "properties": params.get("properties", {})
            }
            return await self._make_request("POST", "/databases", data)
        
        elif tool_name == "query_database":
            return await self._make_request("POST", f"/databases/{database_id}/query", {
                "page_size": params.get("page_size", 10),
                "filter": params.get("filter")
            })
        
        elif tool_name == "append_block_children":
            data = {
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": params.get("content", "")}}]
                        }
                    }
                ]
            }
            return await self._make_request("PATCH", f"/blocks/{page_id}/children", data)
        
        elif tool_name == "list_databases":
            return await self._make_request("POST", "/search", {
                "filter": {"property": "object", "value": "database"},
                "page_size": params.get("page_size", 10)
            })
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "notion://databases":
            return await self._make_request("POST", "/search", {
                "filter": {"property": "object", "value": "database"},
                "page_size": 100
            })
        raise ValueError(f"Unknown resource: {resource.uri}")
