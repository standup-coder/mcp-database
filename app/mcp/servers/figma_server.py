"""
Figma MCP Server
从 Figma 设计文件获取布局/样式信息并下载图片资源
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class FIGMAMCPServer(BaseMCPServer):

    FIGMA_API = "https://api.figma.com/v1"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("FIGMA_API_KEY", ""))
        super().__init__(config)

    def register_tools(self) -> None:
        self._register_tool(MCPTool(
            name="get_figma_data",
            description="获取 Figma 文件的布局、样式和设计 token 信息",
            input_schema={
                "type": "object",
                "properties": {
                    "fileKey": {"type": "string", "description": "Figma 文件 Key（URL 中的标识）"},
                    "nodeId": {"type": "string", "description": "特定节点 ID（可选，不传则获取整个文件）"},
                    "depth": {"type": "integer", "description": "节点树深度限制（可选）"},
                },
                "required": ["fileKey"]
            },
            capability=ServerCapability.READ
        ))
        self._register_tool(MCPTool(
            name="download_figma_images",
            description="从 Figma 节点下载 SVG/PNG 图片到本地项目",
            input_schema={
                "type": "object",
                "properties": {
                    "fileKey": {"type": "string", "description": "Figma 文件 Key"},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "nodeId": {"type": "string"},
                                "fileName": {"type": "string"},
                                "format": {"type": "string", "enum": ["svg", "png", "jpg", "pdf"], "default": "svg"},
                            },
                            "required": ["nodeId"]
                        },
                        "description": "要下载的节点列表"
                    },
                    "localPath": {"type": "string", "description": "本地保存路径"},
                },
                "required": ["fileKey", "nodes", "localPath"]
            },
            capability=ServerCapability.READ
        ))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="figma://status",
            name="Figma 状态",
            description="API 连接状态"
        ))

    def _headers(self) -> Dict[str, str]:
        return {"X-Figma-Token": self.api_key}

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=60) as client:
            if tool_name == "get_figma_data":
                return await self._get_figma_data(client, params)
            elif tool_name == "download_figma_images":
                return await self._download_images(client, params)
            raise ValueError(f"未知工具: {tool_name}")

    async def _get_figma_data(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        file_key = params["fileKey"]
        node_id = params.get("nodeId")
        depth = params.get("depth")

        if node_id:
            url = f"{self.FIGMA_API}/files/{file_key}/nodes"
            query_params: Dict[str, Any] = {"ids": node_id}
            if depth:
                query_params["depth"] = depth
            resp = await client.get(url, params=query_params, headers=self._headers())
        else:
            url = f"{self.FIGMA_API}/files/{file_key}"
            query_params = {}
            if depth:
                query_params["depth"] = depth
            resp = await client.get(url, params=query_params, headers=self._headers())

        resp.raise_for_status()
        data = resp.json()
        return {
            "fileKey": file_key,
            "name": data.get("name", ""),
            "lastModified": data.get("lastModified", ""),
            "version": data.get("version", ""),
            "document": data.get("document") or data.get("nodes"),
        }

    async def _download_images(self, client: httpx.AsyncClient, params: Dict[str, Any]) -> Dict[str, Any]:
        file_key = params["fileKey"]
        nodes = params["nodes"]
        local_path = Path(params["localPath"])
        local_path.mkdir(parents=True, exist_ok=True)

        results = []
        for node in nodes:
            node_id = node["nodeId"]
            fmt = node.get("format", "svg")
            file_name = node.get("fileName", f"{node_id}.{fmt}")

            resp = await client.get(
                f"{self.FIGMA_API}/images/{file_key}",
                params={"ids": node_id, "format": fmt},
                headers=self._headers()
            )
            resp.raise_for_status()
            image_urls = resp.json().get("images", {})
            image_url = image_urls.get(node_id)

            if image_url:
                img_resp = await client.get(image_url)
                img_resp.raise_for_status()
                file_path = local_path / file_name
                file_path.write_bytes(img_resp.content)
                results.append({"nodeId": node_id, "file": str(file_path), "size": len(img_resp.content)})
            else:
                results.append({"nodeId": node_id, "error": "未找到图片 URL"})

        return {"downloaded": len([r for r in results if "error" not in r]), "results": results}

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "figma://status":
            return {"api_key_configured": bool(self.api_key)}
        raise ValueError(f"未知资源: {resource.uri}")
