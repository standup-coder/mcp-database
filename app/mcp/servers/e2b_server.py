"""
E2B MCP Server
安全云端代码执行沙箱，支持 Python 和 JavaScript
"""

import os
from typing import Any, Dict, List, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class E2BMCPServer(BaseMCPServer):

    E2B_API = "https://api.e2b.dev"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("E2B_API_KEY", ""))
        self._default_sandbox: Optional[str] = None
        super().__init__(config)

    def register_tools(self) -> None:
        tools = [
            ("create_sandbox", "创建新的代码执行沙箱环境", {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "enum": ["python", "javascript"], "default": "python"},
                    "timeout": {"type": "integer", "description": "沙箱超时(秒)", "default": 300},
                }
            }, ServerCapability.EXECUTE),
            ("execute_code", "在沙箱中执行代码", {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "代码内容"},
                    "language": {"type": "string", "enum": ["python", "javascript"], "default": "python"},
                    "sandbox_id": {"type": "string", "description": "沙箱 ID（可选，默认使用最近创建的）"},
                },
                "required": ["code"]
            }, ServerCapability.EXECUTE),
            ("create_file", "在沙箱中创建文件", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"},
                    "sandbox_id": {"type": "string"},
                },
                "required": ["path", "content"]
            }, ServerCapability.WRITE),
            ("read_file", "读取沙箱中的文件", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "sandbox_id": {"type": "string"},
                },
                "required": ["path"]
            }, ServerCapability.READ),
            ("list_files", "列出沙箱中的文件", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."},
                    "sandbox_id": {"type": "string"},
                }
            }, ServerCapability.READ),
            ("install_packages", "在沙箱中安装依赖包", {
                "type": "object",
                "properties": {
                    "packages": {"type": "array", "items": {"type": "string"}, "description": "包名列表"},
                    "language": {"type": "string", "enum": ["python", "javascript"], "default": "python"},
                    "sandbox_id": {"type": "string"},
                },
                "required": ["packages"]
            }, ServerCapability.EXECUTE),
            ("get_sandbox_info", "获取沙箱状态和资源使用信息", {
                "type": "object",
                "properties": {
                    "sandbox_id": {"type": "string"},
                }
            }, ServerCapability.READ),
        ]
        for name, desc, schema, cap in tools:
            self._register_tool(MCPTool(name=name, description=desc, input_schema=schema, capability=cap))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="e2b://sandboxes",
            name="活跃沙箱",
            description="当前活跃的沙箱列表"
        ))

    def _headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _sandbox_id(self, params: Dict[str, Any]) -> Optional[str]:
        return params.get("sandbox_id") or self._default_sandbox

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=60) as client:
            dispatch = {
                "create_sandbox": self._create_sandbox,
                "execute_code": self._execute_code,
                "create_file": self._create_file,
                "read_file": self._read_file,
                "list_files": self._list_files,
                "install_packages": self._install_packages,
                "get_sandbox_info": self._get_sandbox_info,
            }
            handler = dispatch.get(tool_name)
            if not handler:
                raise ValueError(f"未知工具: {tool_name}")
            return await handler(client, params)

    async def _create_sandbox(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        language = params.get("language", "python")
        timeout = params.get("timeout", 300)
        template = "base" if language == "python" else "nodejs"

        resp = await client.post(
            f"{self.E2B_API}/sandboxes",
            json={"templateID": template, "timeout": timeout},
            headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        sandbox_id = data.get("sandboxID") or data.get("sandbox_id")
        self._default_sandbox = sandbox_id
        return {"sandbox_id": sandbox_id, "language": language, "timeout": timeout}

    async def _execute_code(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        sandbox_id = self._sandbox_id(params)
        if not sandbox_id:
            return {"error": "无活跃沙箱，请先调用 create_sandbox"}

        language = params.get("language", "python")
        code = params["code"]

        resp = await client.post(
            f"{self.E2B_API}/sandboxes/{sandbox_id}/code",
            json={"code": code, "language": language},
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _create_file(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        sandbox_id = self._sandbox_id(params)
        if not sandbox_id:
            return {"error": "无活跃沙箱"}

        resp = await client.post(
            f"{self.E2B_API}/sandboxes/{sandbox_id}/files",
            json={"path": params["path"], "content": params["content"]},
            headers=self._headers()
        )
        resp.raise_for_status()
        return {"path": params["path"], "status": "created"}

    async def _read_file(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        sandbox_id = self._sandbox_id(params)
        if not sandbox_id:
            return {"error": "无活跃沙箱"}

        resp = await client.get(
            f"{self.E2B_API}/sandboxes/{sandbox_id}/files",
            params={"path": params["path"]},
            headers=self._headers()
        )
        resp.raise_for_status()
        return {"path": params["path"], "content": resp.json().get("content", "")}

    async def _list_files(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        sandbox_id = self._sandbox_id(params)
        if not sandbox_id:
            return {"error": "无活跃沙箱"}

        path = params.get("path", ".")
        resp = await client.get(
            f"{self.E2B_API}/sandboxes/{sandbox_id}/files",
            params={"path": path, "list": "true"},
            headers=self._headers()
        )
        resp.raise_for_status()
        return {"path": path, "files": resp.json()}

    async def _install_packages(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        sandbox_id = self._sandbox_id(params)
        if not sandbox_id:
            return {"error": "无活跃沙箱"}

        packages = params["packages"]
        language = params.get("language", "python")
        cmd = f"pip install {' '.join(packages)}" if language == "python" else f"npm install {' '.join(packages)}"

        resp = await client.post(
            f"{self.E2B_API}/sandboxes/{sandbox_id}/code",
            json={"code": f"import subprocess; subprocess.run('{cmd}', shell=True, capture_output=True)", "language": "python"}
            if language == "python" else
            {"code": f"const {{ execSync }} = require('child_process'); console.log(execSync('{cmd}').toString())", "language": "javascript"},
            headers=self._headers()
        )
        resp.raise_for_status()
        return {"packages": packages, "language": language, "status": "installed"}

    async def _get_sandbox_info(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        sandbox_id = self._sandbox_id(params)
        if not sandbox_id:
            return {"error": "无活跃沙箱"}

        resp = await client.get(
            f"{self.E2B_API}/sandboxes/{sandbox_id}",
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "e2b://sandboxes":
            return {
                "api_key_configured": bool(self.api_key),
                "default_sandbox": self._default_sandbox,
            }
        raise ValueError(f"未知资源: {resource.uri}")
