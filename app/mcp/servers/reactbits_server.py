"""
ReactBits MCP Server
135+ 动画 React 组件库，支持浏览、搜索和获取组件源码
"""

import os
from typing import Any, Dict, List, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class REACTBITSMCPServer(BaseMCPServer):

    REPO_OWNER = "davidhdev"
    REPO_NAME = "react-bits"
    GITHUB_RAW = "https://raw.githubusercontent.com"
    GITHUB_API = "https://api.github.com"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.github_token = cfg.get("github_token", os.environ.get("GITHUB_TOKEN", ""))
        super().__init__(config)

    def register_tools(self) -> None:
        tools = [
            ("list_components", "列出可用的 React 动画组件", {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "组件分类过滤"},
                    "style": {"type": "string", "enum": ["css", "tailwind", "default"], "description": "样式类型"},
                    "limit": {"type": "integer", "default": 20, "description": "最大返回数量"},
                }
            }, ServerCapability.READ),
            ("get_component", "获取组件源码", {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "组件名称"},
                    "style": {"type": "string", "enum": ["css", "tailwind", "default"], "default": "default"},
                },
                "required": ["name"]
            }, ServerCapability.READ),
            ("search_components", "按名称或描述搜索组件", {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "category": {"type": "string", "description": "分类过滤"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["query"]
            }, ServerCapability.READ),
            ("get_component_demo", "获取组件使用示例", {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "组件名称"},
                },
                "required": ["name"]
            }, ServerCapability.READ),
            ("list_categories", "列出所有组件分类", {
                "type": "object", "properties": {}
            }, ServerCapability.READ),
        ]
        for name, desc, schema, cap in tools:
            self._register_tool(MCPTool(name=name, description=desc, input_schema=schema, capability=cap))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="reactbits://catalog",
            name="组件目录",
            description="ReactBits 组件目录树"
        ))

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            dispatch = {
                "list_components": self._list_components,
                "get_component": self._get_component,
                "search_components": self._search_components,
                "get_component_demo": self._get_component_demo,
                "list_categories": self._list_categories,
            }
            handler = dispatch.get(tool_name)
            if not handler:
                raise ValueError(f"未知工具: {tool_name}")
            return await handler(client, params)

    async def _list_components(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        limit = params.get("limit", 20)
        category = params.get("category")
        style = params.get("style", "default")

        resp = await client.get(
            f"{self.GITHUB_API}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/src",
            headers=self._headers()
        )
        if resp.status_code != 200:
            return {"components": [], "error": "无法获取组件目录", "status": resp.status_code}

        items = resp.json()
        components = []
        for item in items:
            if item["type"] != "dir":
                continue
            if category and category.lower() not in item["name"].lower():
                continue
            components.append({"name": item["name"], "path": item["path"], "type": "directory"})
            if len(components) >= limit:
                break

        return {"components": components, "style": style, "count": len(components)}

    async def _get_component(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params["name"]
        style = params.get("style", "default")

        search_path = f"src/{name}"
        resp = await client.get(
            f"{self.GITHUB_API}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/{search_path}",
            headers=self._headers()
        )

        if resp.status_code != 200:
            search_path = f"src/content/{name}"
            resp = await client.get(
                f"{self.GITHUB_API}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/{search_path}",
                headers=self._headers()
            )

        if resp.status_code != 200:
            return {"error": f"组件 '{name}' 未找到"}

        files = resp.json()
        source_files = {}
        if isinstance(files, list):
            for f in files:
                if f["name"].endswith((".jsx", ".tsx", ".css")):
                    raw_resp = await client.get(f["download_url"])
                    if raw_resp.status_code == 200:
                        source_files[f["name"]] = raw_resp.text
        return {"name": name, "style": style, "files": source_files}

    async def _search_components(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params["query"].lower()
        limit = params.get("limit", 10)

        resp = await client.get(
            f"{self.GITHUB_API}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/src",
            headers=self._headers()
        )
        if resp.status_code != 200:
            return {"results": [], "error": "无法获取组件目录"}

        items = resp.json()
        results = []
        for item in items:
            if item["type"] != "dir":
                continue
            if query in item["name"].lower():
                results.append({"name": item["name"], "path": item["path"]})
                if len(results) >= limit:
                    break
        return {"query": params["query"], "results": results, "count": len(results)}

    async def _get_component_demo(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params["name"]
        demo_path = f"src/content/{name}/Demo.jsx"
        resp = await client.get(
            f"{self.GITHUB_RAW}/{self.REPO_OWNER}/{self.REPO_NAME}/main/{demo_path}",
            headers=self._headers()
        )
        if resp.status_code == 200:
            return {"name": name, "demo": resp.text}

        demo_path = f"src/content/{name}/Demo.tsx"
        resp = await client.get(
            f"{self.GITHUB_RAW}/{self.REPO_OWNER}/{self.REPO_NAME}/main/{demo_path}",
            headers=self._headers()
        )
        if resp.status_code == 200:
            return {"name": name, "demo": resp.text}

        return {"name": name, "error": "未找到 Demo 文件"}

    async def _list_categories(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = await client.get(
            f"{self.GITHUB_API}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/src/content",
            headers=self._headers()
        )
        if resp.status_code != 200:
            return {"categories": [], "error": "无法获取分类目录"}
        categories = [item["name"] for item in resp.json() if item["type"] == "dir"]
        return {"categories": categories, "count": len(categories)}

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "reactbits://catalog":
            return {"repo": f"{self.REPO_OWNER}/{self.REPO_NAME}", "source": "GitHub"}
        raise ValueError(f"未知资源: {resource.uri}")
