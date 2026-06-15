"""
Sentry MCP Server
错误监控与调试工具，集成 Sentry Issues、Events 和项目管理
"""

import os
import re
from typing import Any, Dict, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class SENTRYMCPServer(BaseMCPServer):

    SENTRY_API = "https://sentry.io/api/0"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.access_token = cfg.get("access_token", os.environ.get("SENTRY_ACCESS_TOKEN", ""))
        self.host = cfg.get("host", os.environ.get("SENTRY_HOST", "sentry.io"))
        if self.host != "sentry.io":
            self.SENTRY_API = f"https://{self.host}/api/0"
        super().__init__(config)

    def register_tools(self) -> None:
        tools = [
            ("list_projects", "列出 Sentry 组织中所有可访问的项目", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string", "description": "组织标识"},
                },
                "required": ["organization_slug"]
            }, ServerCapability.READ),
            ("get_issue", "获取 Sentry Issue 详情，包含堆栈跟踪和面包屑", {
                "type": "object",
                "properties": {
                    "issue_id_or_url": {"type": "string", "description": "Issue ID 或完整 URL"},
                },
                "required": ["issue_id_or_url"]
            }, ServerCapability.READ),
            ("list_project_issues", "列出指定项目的 Issues", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string"},
                    "project_slug": {"type": "string"},
                    "query": {"type": "string", "description": "Sentry 搜索查询"},
                    "limit": {"type": "integer", "default": 25},
                },
                "required": ["organization_slug", "project_slug"]
            }, ServerCapability.READ),
            ("get_event", "获取 Issue 下某个具体事件的详情", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string"},
                    "project_slug": {"type": "string"},
                    "event_id": {"type": "string"},
                },
                "required": ["organization_slug", "project_slug", "event_id"]
            }, ServerCapability.READ),
            ("search_issues", "搜索 Sentry Issues", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string"},
                    "query": {"type": "string", "description": "搜索查询"},
                    "project_slug": {"type": "string"},
                },
                "required": ["organization_slug", "query"]
            }, ServerCapability.READ),
            ("list_issue_events", "列出 Issue 的所有事件", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string"},
                    "project_slug": {"type": "string"},
                    "issue_id": {"type": "string"},
                },
                "required": ["organization_slug", "project_slug", "issue_id"]
            }, ServerCapability.READ),
            ("resolve_short_id", "通过短 ID 解析 Issue", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string"},
                    "short_id": {"type": "string", "description": "如 PROJECT-123"},
                },
                "required": ["organization_slug", "short_id"]
            }, ServerCapability.READ),
            ("create_project", "在 Sentry 中创建新项目", {
                "type": "object",
                "properties": {
                    "organization_slug": {"type": "string"},
                    "team_slug": {"type": "string"},
                    "name": {"type": "string"},
                    "platform": {"type": "string", "description": "平台（如 python, javascript, node）"},
                },
                "required": ["organization_slug", "team_slug", "name"]
            }, ServerCapability.WRITE),
        ]
        for name, desc, schema, cap in tools:
            self._register_tool(MCPTool(name=name, description=desc, input_schema=schema, capability=cap))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="sentry://status",
            name="Sentry 状态",
            description="API 连接状态"
        ))

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def _extract_issue_id(self, issue_id_or_url: str) -> str:
        if issue_id_or_url.startswith("http"):
            match = re.search(r"/issues/(\d+)", issue_id_or_url)
            if match:
                return match.group(1)
        return issue_id_or_url

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            dispatch = {
                "list_projects": self._list_projects,
                "get_issue": self._get_issue,
                "list_project_issues": self._list_project_issues,
                "get_event": self._get_event,
                "search_issues": self._search_issues,
                "list_issue_events": self._list_issue_events,
                "resolve_short_id": self._resolve_short_id,
                "create_project": self._create_project,
            }
            handler = dispatch.get(tool_name)
            if not handler:
                raise ValueError(f"未知工具: {tool_name}")
            return await handler(client, params)

    async def _list_projects(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        resp = await client.get(f"{self.SENTRY_API}/organizations/{org}/projects/", headers=self._headers())
        resp.raise_for_status()
        projects = resp.json()
        return {"organization": org, "projects": [{"id": p["id"], "slug": p["slug"], "name": p["name"], "platform": p.get("platform")} for p in projects]}

    async def _get_issue(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        issue_id = self._extract_issue_id(params["issue_id_or_url"])
        resp = await client.get(f"{self.SENTRY_API}/issues/{issue_id}/", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def _list_project_issues(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        project = params["project_slug"]
        query_params: Dict[str, Any] = {"limit": params.get("limit", 25)}
        if params.get("query"):
            query_params["query"] = params["query"]
        resp = await client.get(
            f"{self.SENTRY_API}/projects/{org}/{project}/issues/",
            params=query_params, headers=self._headers()
        )
        resp.raise_for_status()
        return {"organization": org, "project": project, "issues": resp.json()}

    async def _get_event(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        project = params["project_slug"]
        event_id = params["event_id"]
        resp = await client.get(
            f"{self.SENTRY_API}/projects/{org}/{project}/events/{event_id}/",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _search_issues(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        query_params: Dict[str, Any] = {"query": params["query"]}
        if params.get("project_slug"):
            query_params["project"] = params["project_slug"]
        resp = await client.get(
            f"{self.SENTRY_API}/organizations/{org}/issues/",
            params=query_params, headers=self._headers()
        )
        resp.raise_for_status()
        return {"organization": org, "query": params["query"], "issues": resp.json()}

    async def _list_issue_events(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        project = params["project_slug"]
        issue_id = params["issue_id"]
        resp = await client.get(
            f"{self.SENTRY_API}/projects/{org}/{project}/issues/{issue_id}/events/",
            headers=self._headers()
        )
        resp.raise_for_status()
        return {"issue_id": issue_id, "events": resp.json()}

    async def _resolve_short_id(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        resp = await client.get(
            f"{self.SENTRY_API}/organizations/{org}/shortids/{params['short_id']}/",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _create_project(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        org = params["organization_slug"]
        team = params["team_slug"]
        body: Dict[str, Any] = {"name": params["name"]}
        if params.get("platform"):
            body["platform"] = params["platform"]
        resp = await client.post(
            f"{self.SENTRY_API}/teams/{org}/{team}/projects/",
            json=body, headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "sentry://status":
            return {"token_configured": bool(self.access_token), "host": self.host}
        raise ValueError(f"未知资源: {resource.uri}")
