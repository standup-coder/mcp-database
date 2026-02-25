"""
Git MCP服务器
提供Git操作功能
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class GitMCPServer(BaseMCPServer):
    """Git MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.repo_path = Path(config.get("repo_path", ".") if config else ".")
        super().__init__(config)
    
    def register_tools(self):
        """注册Git操作工具"""
        self._register_tool(MCPTool(
            name="status",
            description="获取Git状态",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="log",
            description="获取Git提交日志",
            input_schema={
                "type": "object",
                "properties": {
                    "max_count": {"type": "integer", "default": 10},
                    "format": {"type": "string", "default": "%h %s"}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="branch",
            description="获取分支列表",
            input_schema={
                "type": "object",
                "properties": {
                    "all": {"type": "boolean", "default": False}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="diff",
            description="获取文件差异",
            input_schema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "文件路径"},
                    "cached": {"type": "boolean", "default": False}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="commit",
            description="提交更改",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "提交信息"},
                    "all": {"type": "boolean", "default": False}
                },
                "required": ["message"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="push",
            description="推送到远程",
            input_schema={
                "type": "object",
                "properties": {
                    "remote": {"type": "string", "default": "origin"},
                    "branch": {"type": "string", "default": "main"}
                },
                "required": []
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="pull",
            description="拉取远程更改",
            input_schema={
                "type": "object",
                "properties": {
                    "remote": {"type": "string", "default": "origin"},
                    "branch": {"type": "string", "default": "main"}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="checkout",
            description="切换分支或检出文件",
            input_schema={
                "type": "object",
                "properties": {
                    "branch": {"type": "string", "description": "分支名"},
                    "file": {"type": "string", "description": "文件路径"},
                    "create": {"type": "boolean", "default": False}
                },
                "required": []
            },
            capability=ServerCapability.EXECUTE
        ))
        
        self._register_tool(MCPTool(
            name="stash",
            description="暂存更改",
            input_schema={
                "type": "object",
                "properties": {
                    "pop": {"type": "boolean", "default": False},
                    "list": {"type": "boolean", "default": False},
                    "message": {"type": "string", "description": "暂存信息"}
                },
                "required": []
            },
            capability=ServerCapability.WRITE
        ))
    
    def register_resources(self):
        """注册Git资源"""
        self._register_resource(MCPResource(
            uri="git://branch",
            name="current_branch",
            description="当前分支"
        ))
        self._register_resource(MCPResource(
            uri="git://remote",
            name="remote_urls",
            description="远程仓库URL"
        ))
    
    def _run_git(self, *args: str) -> str:
        """执行Git命令"""
        result = subprocess.run(
            ["git"] + list(args),
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")
        return result.stdout
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行Git操作"""
        if tool_name == "status":
            return self._run_git("status", "--porcelain")
        
        elif tool_name == "log":
            max_count = params.get("max_count", 10)
            format_str = params.get("format", "%h %s")
            return self._run_git("log", f"--max-count={max_count}", f"--format={format_str}")
        
        elif tool_name == "branch":
            all_branches = params.get("all", False)
            args = ["branch"]
            if all_branches:
                args.append("-a")
            return self._run_git(*args)
        
        elif tool_name == "diff":
            file = params.get("file")
            cached = params.get("cached", False)
            args = ["diff"]
            if cached:
                args.append("--cached")
            if file:
                args.append("--")
                args.append(file)
            return self._run_git(*args)
        
        elif tool_name == "commit":
            message = params.get("message", "")
            all_files = params.get("all", False)
            args = ["commit", "-m", message]
            if all_files:
                args.insert(1, "-a")
            return self._run_git(*args)
        
        elif tool_name == "push":
            remote = params.get("remote", "origin")
            branch = params.get("branch", "main")
            return self._run_git("push", remote, branch)
        
        elif tool_name == "pull":
            remote = params.get("remote", "origin")
            branch = params.get("branch", "main")
            return self._run_git("pull", remote, branch)
        
        elif tool_name == "checkout":
            branch = params.get("branch")
            file = params.get("file")
            create = params.get("create", False)
            
            if branch and create:
                return self._run_git("checkout", "-b", branch)
            elif branch:
                return self._run_git("checkout", branch)
            elif file:
                return self._run_git("checkout", "--", file)
        
        elif tool_name == "stash":
            if params.get("list"):
                return self._run_git("stash", "list")
            elif params.get("pop"):
                return self._run_git("stash", "pop")
            else:
                message = params.get("message", "")
                return self._run_git("stash", "push", "-m", message)
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "git://branch":
            return self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        elif resource.uri == "git://remote":
            return self._run_git("remote", "-v")
        raise ValueError(f"Unknown resource: {resource.uri}")
