"""
Linear MCP Server
项目管理与 Issue 跟踪工具，集成 Linear 的 Issue CRUD 和评论功能
"""

import os
from typing import Any, Dict, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class LINEARMCPServer(BaseMCPServer):

    LINEAR_API = "https://api.linear.app/graphql"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("LINEAR_API_KEY", ""))
        super().__init__(config)

    def register_tools(self) -> None:
        tools = [
            ("create_issue", "创建 Linear Issue", {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Issue 标题"},
                    "teamId": {"type": "string", "description": "团队 ID"},
                    "description": {"type": "string", "description": "Issue 描述（Markdown）"},
                    "priority": {"type": "integer", "description": "优先级 0-4（0=无, 1=紧急, 4=低）", "minimum": 0, "maximum": 4},
                    "status": {"type": "string", "description": "状态名称"},
                },
                "required": ["title", "teamId"]
            }, ServerCapability.WRITE),
            ("update_issue", "更新现有 Issue", {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Issue ID"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                    "status": {"type": "string"},
                },
                "required": ["id"]
            }, ServerCapability.WRITE),
            ("search_issues", "搜索和过滤 Issues", {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "teamId": {"type": "string"},
                    "status": {"type": "string"},
                    "assigneeId": {"type": "string"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                    "limit": {"type": "integer", "default": 10},
                }
            }, ServerCapability.READ),
            ("get_user_issues", "获取分配给用户的 Issues", {
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "用户 ID（可选，默认当前用户）"},
                    "includeArchived": {"type": "boolean", "default": False},
                    "limit": {"type": "integer", "default": 50},
                }
            }, ServerCapability.READ),
            ("add_comment", "为 Issue 添加评论", {
                "type": "object",
                "properties": {
                    "issueId": {"type": "string", "description": "Issue ID"},
                    "body": {"type": "string", "description": "评论内容（Markdown）"},
                },
                "required": ["issueId", "body"]
            }, ServerCapability.WRITE),
        ]
        for name, desc, schema, cap in tools:
            self._register_tool(MCPTool(name=name, description=desc, input_schema=schema, capability=cap))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="linear://status",
            name="Linear 状态",
            description="API 连接状态"
        ))

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    async def _graphql(self, client: httpx.AsyncClient, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        resp = await client.post(
            self.LINEAR_API,
            json={"query": query, "variables": variables or {}},
            headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            return {"error": data["errors"][0]["message"]}
        return data.get("data", {})

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            dispatch = {
                "create_issue": self._create_issue,
                "update_issue": self._update_issue,
                "search_issues": self._search_issues,
                "get_user_issues": self._get_user_issues,
                "add_comment": self._add_comment,
            }
            handler = dispatch.get(tool_name)
            if not handler:
                raise ValueError(f"未知工具: {tool_name}")
            return await handler(client, params)

    async def _create_issue(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        input_fields = f'teamId: "{params["teamId"]}", title: "{params["title"]}"'
        if params.get("description"):
            desc = params["description"].replace('"', '\\"')
            input_fields += f', description: "{desc}"'
        if params.get("priority") is not None:
            input_fields += f', priority: {params["priority"]}'

        query = f'mutation {{ issueCreate(input: {{ {input_fields} }}) {{ success issue {{ id title identifier url }} }} }}'
        data = await self._graphql(client, query)
        return data.get("issueCreate", {})

    async def _update_issue(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        input_parts = []
        if params.get("title"):
            input_parts.append(f'title: "{params["title"]}"')
        if params.get("description"):
            desc = params["description"].replace('"', '\\"')
            input_parts.append(f'description: "{desc}"')
        if params.get("priority") is not None:
            input_parts.append(f'priority: {params["priority"]}')

        if not input_parts:
            return {"error": "至少需要一个更新字段"}

        input_str = ", ".join(input_parts)
        query = f'mutation {{ issueUpdate(id: "{params["id"]}", input: {{ {input_str} }}) {{ success issue {{ id title identifier }} }} }}'
        data = await self._graphql(client, query)
        return data.get("issueUpdate", {})

    async def _search_issues(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        limit = params.get("limit", 10)
        filter_parts = []
        if params.get("query"):
            q = params["query"].replace('"', '\\"')
            filter_parts.append(f'title: {{ contains: "{q}" }}')
        if params.get("teamId"):
            filter_parts.append(f'team: {{ id: {{ eq: "{params["teamId"]}" }} }}')
        if params.get("priority") is not None:
            filter_parts.append(f'priority: {{ eq: {params["priority"]} }}')

        filter_str = f'filter: {{ {", ".join(filter_parts)} }}' if filter_parts else ""
        query = f'{{ issues(first: {limit} {filter_str}) {{ nodes {{ id title identifier priority state {{ name }} assignee {{ name }} url }} }} }}'
        data = await self._graphql(client, query)
        return data.get("issues", {})

    async def _get_user_issues(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        limit = params.get("limit", 50)
        query = f'{{ viewer {{ assignedIssues(first: {limit}) {{ nodes {{ id title identifier priority state {{ name }} url }} }} }} }}'
        data = await self._graphql(client, query)
        viewer = data.get("viewer", {})
        return viewer.get("assignedIssues", {})

    async def _add_comment(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Any:
        body = params["body"].replace('"', '\\"')
        query = f'mutation {{ commentCreate(input: {{ issueId: "{params["issueId"]}", body: "{body}" }}) {{ success comment {{ id body createdAt }} }} }}'
        data = await self._graphql(client, query)
        return data.get("commentCreate", {})

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "linear://status":
            return {"api_key_configured": bool(self.api_key)}
        raise ValueError(f"未知资源: {resource.uri}")
