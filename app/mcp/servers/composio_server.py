"""
Composio MCP Server
多平台集成工具，通过统一 API 访问 500+ 应用（GitHub、Slack、Gmail、Jira 等）
"""

import os
from typing import Any, Dict, List, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class COMPOSIOMCPServer(BaseMCPServer):

    COMPOSIO_API = "https://backend.composio.dev/api/v1"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("COMPOSIO_API_KEY", ""))
        super().__init__(config)

    def register_tools(self) -> None:
        tools = [
            ("search_tools", "在 500+ 应用中搜索可用工具", {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "toolkit": {"type": "string", "description": "工具包名称过滤（如 github, slack）"},
                },
                "required": ["query"]
            }, ServerCapability.READ),
            ("execute_action", "执行 Composio 工具操作", {
                "type": "object",
                "properties": {
                    "action_name": {"type": "string", "description": "操作名称（如 GITHUB_CREATE_ISSUE）"},
                    "params": {"type": "object", "description": "操作参数"},
                    "connection_id": {"type": "string", "description": "连接 ID（可选）"},
                },
                "required": ["action_name"]
            }, ServerCapability.EXECUTE),
            ("list_toolkits", "列出所有可用的工具包", {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "分类过滤"},
                }
            }, ServerCapability.READ),
            ("initiate_connection", "发起应用 OAuth 连接", {
                "type": "object",
                "properties": {
                    "toolkit_name": {"type": "string", "description": "工具包名称（如 github, slack）"},
                },
                "required": ["toolkit_name"]
            }, ServerCapability.WRITE),
            ("list_connections", "列出所有活跃的应用连接", {
                "type": "object", "properties": {}
            }, ServerCapability.READ),
            ("get_tool_schema", "获取工具的输入/输出 Schema", {
                "type": "object",
                "properties": {
                    "tool_slug": {"type": "string", "description": "工具标识符"},
                },
                "required": ["tool_slug"]
            }, ServerCapability.READ),
        ]
        for name, desc, schema, cap in tools:
            self._register_tool(MCPTool(name=name, description=desc, input_schema=schema, capability=cap))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="composio://connections",
            name="活跃连接",
            description="当前活跃的应用连接列表"
        ))

    def _headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            dispatch = {
                "search_tools": self._search_tools,
                "execute_action": self._execute_action,
                "list_toolkits": self._list_toolkits,
                "initiate_connection": self._initiate_connection,
                "list_connections": self._list_connections,
                "get_tool_schema": self._get_tool_schema,
            }
            handler = dispatch.get(tool_name)
            if not handler:
                raise ValueError(f"未知工具: {tool_name}")
            return await handler(client, params)

    async def _search_tools(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        query_params: Dict[str, Any] = {"q": params["query"]}
        if params.get("toolkit"):
            query_params["toolkit"] = params["toolkit"]
        resp = await client.get(
            f"{self.COMPOSIO_API}/tools/search",
            params=query_params, headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _execute_action(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        body: Dict[str, Any] = {
            "actionName": params["action_name"],
            "input": params.get("params", {}),
        }
        if params.get("connection_id"):
            body["connectedAccountId"] = params["connection_id"]

        resp = await client.post(
            f"{self.COMPOSIO_API}/actions/execute",
            json=body, headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _list_toolkits(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        query_params = {}
        if params.get("category"):
            query_params["category"] = params["category"]
        resp = await client.get(
            f"{self.COMPOSIO_API}/toolkits",
            params=query_params, headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _initiate_connection(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        resp = await client.post(
            f"{self.COMPOSIO_API}/connectedAccounts/integration",
            json={"integrationName": params["toolkit_name"]},
            headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "toolkit": params["toolkit_name"],
            "connection_id": data.get("connectedAccountId"),
            "redirect_url": data.get("redirectUrl"),
            "status": data.get("status"),
        }

    async def _list_connections(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        resp = await client.get(
            f"{self.COMPOSIO_API}/connectedAccounts",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _get_tool_schema(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        resp = await client.get(
            f"{self.COMPOSIO_API}/tools/{params['tool_slug']}",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "composio://connections":
            if not self.api_key:
                return {"error": "COMPOSIO_API_KEY 未配置"}
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(f"{self.COMPOSIO_API}/connectedAccounts", headers=self._headers())
                    resp.raise_for_status()
                    return {"connections": resp.json()}
            except Exception as e:
                return {"error": str(e)}
        raise ValueError(f"未知资源: {resource.uri}")
