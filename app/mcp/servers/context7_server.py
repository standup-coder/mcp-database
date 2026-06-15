"""
Context7 MCP Server
版本精确文档注入工具，查询特定版本的库文档
"""

import os
from typing import Any, Dict, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class CONTEXT7MCPServer(BaseMCPServer):

    BASE_URL = "https://mcp.context7.com"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("CONTEXT7_API_KEY", ""))
        super().__init__(config)

    def register_tools(self) -> None:
        self._register_tool(MCPTool(
            name="resolve_library_id",
            description="将通用库名解析为 Context7 兼容的库 ID（如 /mongodb/docs）",
            input_schema={
                "type": "object",
                "properties": {
                    "libraryName": {"type": "string", "description": "库名称（如 react, next.js, django）"},
                    "query": {"type": "string", "description": "查询上下文，帮助精确匹配"},
                },
                "required": ["libraryName", "query"]
            },
            capability=ServerCapability.READ
        ))
        self._register_tool(MCPTool(
            name="query_docs",
            description="获取特定库版本精确的文档内容",
            input_schema={
                "type": "object",
                "properties": {
                    "libraryId": {"type": "string", "description": "Context7 库 ID（如 /mongodb/docs）"},
                    "query": {"type": "string", "description": "文档查询内容"},
                },
                "required": ["libraryId", "query"]
            },
            capability=ServerCapability.READ
        ))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="context7://status",
            name="Context7 状态",
            description="API 连接状态"
        ))

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            if tool_name == "resolve_library_id":
                resp = await client.post(
                    f"{self.BASE_URL}/resolve",
                    json={"libraryName": params["libraryName"], "query": params["query"]},
                    headers=self._headers()
                )
                resp.raise_for_status()
                return resp.json()

            elif tool_name == "query_docs":
                resp = await client.post(
                    f"{self.BASE_URL}/query",
                    json={"libraryId": params["libraryId"], "query": params["query"]},
                    headers=self._headers()
                )
                resp.raise_for_status()
                return resp.json()

            raise ValueError(f"未知工具: {tool_name}")

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "context7://status":
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(f"{self.BASE_URL}/health")
                    return {"status": "connected" if resp.status_code == 200 else "degraded", "api_key": bool(self.api_key)}
            except Exception:
                return {"status": "disconnected", "api_key": bool(self.api_key)}
        raise ValueError(f"未知资源: {resource.uri}")
