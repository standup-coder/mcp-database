"""
Docfork MCP Server
文档同步查询工具，搜索 9000+ 库的最新文档并获取 Markdown 全文
"""

import os
from typing import Any, Dict, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class DOCFORKMCPServer(BaseMCPServer):

    BASE_URL = "https://mcp.docfork.com"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("DOCFORK_API_KEY", ""))
        super().__init__(config)

    def register_tools(self) -> None:
        self._register_tool(MCPTool(
            name="search_docs",
            description="在 9000+ 库的文档中搜索相关内容，返回排序的文档片段",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询内容"},
                    "library": {"type": "string", "description": "库名称或关键词（如 react, django, fastapi）"},
                },
                "required": ["query", "library"]
            },
            capability=ServerCapability.READ
        ))
        self._register_tool(MCPTool(
            name="fetch_doc",
            description="获取文档页面的完整 Markdown 内容",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "文档页面 URL（来自搜索结果）"},
                },
                "required": ["url"]
            },
            capability=ServerCapability.READ
        ))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="docfork://status",
            name="Docfork 状态",
            description="API 连接状态"
        ))

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            if tool_name == "search_docs":
                resp = await client.post(
                    f"{self.BASE_URL}/search",
                    json={"query": params["query"], "library": params["library"]},
                    headers=self._headers()
                )
                resp.raise_for_status()
                return resp.json()

            elif tool_name == "fetch_doc":
                resp = await client.post(
                    f"{self.BASE_URL}/fetch",
                    json={"url": params["url"]},
                    headers=self._headers()
                )
                resp.raise_for_status()
                return resp.json()

            raise ValueError(f"未知工具: {tool_name}")

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "docfork://status":
            return {"api_key_configured": bool(self.api_key), "base_url": self.BASE_URL}
        raise ValueError(f"未知资源: {resource.uri}")
