"""
DeepWiki MCP Server
将 deepwiki.com 文档页面转换为结构化 Markdown
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class DEEPWIKIMCPServer(BaseMCPServer):

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.max_concurrency = int(cfg.get("max_concurrency", os.environ.get("DEEPWIKI_MAX_CONCURRENCY", "5")))
        self.request_timeout = int(cfg.get("request_timeout", os.environ.get("DEEPWIKI_REQUEST_TIMEOUT", "30000")))
        self.max_retries = int(cfg.get("max_retries", os.environ.get("DEEPWIKI_MAX_RETRIES", "3")))
        self.retry_delay = int(cfg.get("retry_delay", os.environ.get("DEEPWIKI_RETRY_DELAY", "250")))
        super().__init__(config)

    def register_tools(self) -> None:
        self._register_tool(MCPTool(
            name="deepwiki_fetch",
            description=(
                "抓取 deepwiki.com 文档页面并转换为干净的 Markdown。"
                "支持 aggregate 模式（单文档）和 pages 模式（结构化数据）。"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "DeepWiki 仓库 URL（如 https://deepwiki.com/facebook/react）"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["aggregate", "pages"],
                        "default": "aggregate",
                        "description": "aggregate=合并为单 Markdown，pages=返回各页面结构化数据"
                    },
                    "maxDepth": {
                        "type": "integer",
                        "default": 10,
                        "description": "最大抓取深度"
                    },
                },
                "required": ["url"]
            },
            capability=ServerCapability.READ
        ))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="deepwiki://config",
            name="DeepWiki 配置",
            description="当前抓取配置参数"
        ))

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        if tool_name != "deepwiki_fetch":
            raise ValueError(f"未知工具: {tool_name}")

        url = params["url"]
        mode = params.get("mode", "aggregate")
        max_depth = params.get("maxDepth", 10)

        parsed = urlparse(url)
        if "deepwiki.com" not in parsed.netloc:
            url = f"https://deepwiki.com/{url.lstrip('/')}"

        pages = await self._fetch_pages(url, max_depth)

        if mode == "aggregate":
            combined = []
            for page in pages:
                combined.append(f"# {page['title']}\n\n{page['content']}")
            return {
                "url": url,
                "mode": "aggregate",
                "pages_fetched": len(pages),
                "markdown": "\n\n---\n\n".join(combined),
            }
        else:
            return {
                "url": url,
                "mode": "pages",
                "pages": pages,
                "count": len(pages),
            }

    async def _fetch_pages(self, base_url: str, max_depth: int) -> List[Dict[str, str]]:
        semaphore = asyncio.Semaphore(self.max_concurrency)
        pages = []

        async with httpx.AsyncClient(
            timeout=self.request_timeout / 1000,
            follow_redirects=True
        ) as client:
            async def fetch_with_retry(url: str, retries: int = 0) -> Optional[Dict[str, str]]:
                async with semaphore:
                    try:
                        resp = await client.get(url, headers={"User-Agent": "mcp4coder-deepwiki/1.0"})
                        resp.raise_for_status()
                        return {"title": url.split("/")[-1], "url": url, "content": resp.text}
                    except httpx.HTTPError:
                        if retries < self.max_retries:
                            await asyncio.sleep(self.retry_delay * (retries + 1) / 1000)
                            return await fetch_with_retry(url, retries + 1)
                        return None

            index_resp = await client.get(base_url, headers={"User-Agent": "mcp4coder-deepwiki/1.0"})
            if index_resp.status_code == 200:
                pages.append({"title": "index", "url": base_url, "content": index_resp.text})

        return pages

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "deepwiki://config":
            return {
                "max_concurrency": self.max_concurrency,
                "request_timeout": self.request_timeout,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
            }
        raise ValueError(f"未知资源: {resource.uri}")
