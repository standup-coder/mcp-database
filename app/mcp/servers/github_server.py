"""
GitHub MCP服务器
提供GitHub API操作功能
"""

import os
import json
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class GitHubMCPServer(BaseMCPServer):
    """GitHub MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.token = config.get("token", os.environ.get("GITHUB_TOKEN", ""))
        self.base_url = "https://api.github.com"
        super().__init__(config)
    
    def register_tools(self):
        """注册GitHub操作工具"""
        self._register_tool(MCPTool(
            name="get_user",
            description="获取当前用户信息",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="list_repos",
            description="列出用户仓库",
            input_schema={
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1},
                    "per_page": {"type": "integer", "default": 30}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_repo",
            description="获取仓库信息",
            input_schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名"}
                },
                "required": ["owner", "repo"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="list_issues",
            description="列出仓库Issues",
            input_schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名"},
                    "state": {"type": "string", "default": "open"},
                    "page": {"type": "integer", "default": 1}
                },
                "required": ["owner", "repo"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="create_issue",
            description="创建Issue",
            input_schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名"},
                    "title": {"type": "string", "description": "标题"},
                    "body": {"type": "string", "description": "内容"}
                },
                "required": ["owner", "repo", "title"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="list_pulls",
            description="列出仓库Pull Requests",
            input_schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名"},
                    "state": {"type": "string", "default": "open"}
                },
                "required": ["owner", "repo"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_file_content",
            description="获取仓库文件内容",
            input_schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名"},
                    "path": {"type": "string", "description": "文件路径"},
                    "ref": {"type": "string", "description": "分支/标签"}
                },
                "required": ["owner", "repo", "path"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="search_code",
            description="搜索代码",
            input_schema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "搜索查询"},
                    "page": {"type": "integer", "default": 1},
                    "per_page": {"type": "integer", "default": 30}
                },
                "required": ["q"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="search_repos",
            description="搜索仓库",
            input_schema={
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "搜索查询"},
                    "page": {"type": "integer", "default": 1},
                    "per_page": {"type": "integer", "default": 30}
                },
                "required": ["q"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="list_commits",
            description="获取提交历史",
            input_schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名"},
                    "per_page": {"type": "integer", "default": 30}
                },
                "required": ["owner", "repo"]
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册GitHub资源"""
        self._register_resource(MCPResource(
            uri="github://user",
            name="current_user",
            description="当前用户信息"
        ))
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """发送GitHub API请求"""
        import base64
        import httpx
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}" if self.token else ""
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 404:
                raise ValueError("Resource not found")
            elif response.status_code >= 400:
                raise ValueError(f"GitHub API error: {response.text}")
            
            if response.text:
                return response.json()
            return None
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行GitHub操作"""
        owner = params.get("owner", "")
        repo = params.get("repo", "")
        
        if tool_name == "get_user":
            return await self._make_request("GET", "/user")
        
        elif tool_name == "list_repos":
            page = params.get("page", 1)
            per_page = params.get("per_page", 30)
            return await self._make_request("GET", f"/user/repos?page={page}&per_page={per_page}")
        
        elif tool_name == "get_repo":
            return await self._make_request("GET", f"/repos/{owner}/{repo}")
        
        elif tool_name == "list_issues":
            state = params.get("state", "open")
            page = params.get("page", 1)
            return await self._make_request("GET", f"/repos/{owner}/{repo}/issues?state={state}&page={page}")
        
        elif tool_name == "create_issue":
            data = {
                "title": params.get("title", ""),
                "body": params.get("body", "")
            }
            return await self._make_request("POST", f"/repos/{owner}/{repo}/issues", data)
        
        elif tool_name == "list_pulls":
            state = params.get("state", "open")
            return await self._make_request("GET", f"/repos/{owner}/{repo}/pulls?state={state}")
        
        elif tool_name == "get_file_content":
            path = params.get("path", "")
            ref = params.get("ref", "")
            endpoint = f"/repos/{owner}/{repo}/contents/{path}"
            if ref:
                endpoint += f"?ref={ref}"
            result = await self._make_request("GET", endpoint)
            if result and result.get("content"):
                import base64
                return {
                    "content": base64.b64decode(result["content"]).decode("utf-8"),
                    "encoding": result["encoding"],
                    "sha": result["sha"]
                }
            return result
        
        elif tool_name == "search_code":
            q = params.get("q", "")
            page = params.get("page", 1)
            per_page = params.get("per_page", 30)
            return await self._make_request("GET", f"/search/code?q={q}&page={page}&per_page={per_page}")
        
        elif tool_name == "search_repos":
            q = params.get("q", "")
            page = params.get("page", 1)
            per_page = params.get("per_page", 30)
            return await self._make_request("GET", f"/search/repositories?q={q}&page={page}&per_page={per_page}")
        
        elif tool_name == "list_commits":
            per_page = params.get("per_page", 30)
            return await self._make_request("GET", f"/repos/{owner}/{repo}/commits?per_page={per_page}")
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "github://user":
            return await self._make_request("GET", "/user")
        raise ValueError(f"Unknown resource: {resource.uri}")
