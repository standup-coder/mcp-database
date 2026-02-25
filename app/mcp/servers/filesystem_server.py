"""
文件系统MCP服务器
提供文件读写、目录操作等功能
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class FilesystemMCPServer(BaseMCPServer):
    """文件系统MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.base_path = Path(config.get("base_path", ".") if config else ".")
        super().__init__(config)
    
    def register_tools(self):
        """注册文件操作工具"""
        self._register_tool(MCPTool(
            name="read_file",
            description="读取文件内容",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="write_file",
            description="写入文件内容",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path", "content"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="list_directory",
            description="列出目录内容",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径"},
                    "recursive": {"type": "boolean", "default": False}
                },
                "required": ["path"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="create_directory",
            description="创建目录",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径"},
                    "parents": {"type": "boolean", "default": True}
                },
                "required": ["path"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="delete_file",
            description="删除文件或目录",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件/目录路径"},
                    "recursive": {"type": "boolean", "default": False}
                },
                "required": ["path"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="search_files",
            description="搜索文件",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "搜索模式"},
                    "path": {"type": "string", "description": "搜索目录"},
                    "file_type": {"type": "string", "description": "文件类型过滤"}
                },
                "required": ["pattern"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_file_info",
            description="获取文件信息",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"]
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册文件系统资源"""
        self._register_resource(MCPResource(
            uri="filesystem://cwd",
            name="current_working_directory",
            description="当前工作目录"
        ))
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行文件操作"""
        path = self._resolve_path(params.get("path", ""))
        
        if tool_name == "read_file":
            encoding = params.get("encoding", "utf-8")
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {path}")
            return path.read_text(encoding=encoding)
        
        elif tool_name == "write_file":
            encoding = params.get("encoding", "utf-8")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(params.get("content", ""), encoding=encoding)
            return {"success": True, "path": str(path)}
        
        elif tool_name == "list_directory":
            recursive = params.get("recursive", False)
            if not path.is_dir():
                raise NotADirectoryError(f"不是目录: {path}")
            
            items = []
            if recursive:
                for item in path.rglob("*"):
                    items.append({
                        "path": str(item.relative_to(path)),
                        "type": "directory" if item.is_dir() else "file",
                        "name": item.name
                    })
            else:
                for item in path.iterdir():
                    items.append({
                        "type": "directory" if item.is_dir() else "file",
                        "name": item.name
                    })
            return items
        
        elif tool_name == "create_directory":
            parents = params.get("parents", True)
            path.mkdir(parents=parents, exist_ok=True)
            return {"success": True, "path": str(path)}
        
        elif tool_name == "delete_file":
            recursive = params.get("recursive", False)
            if path.is_dir():
                import shutil
                shutil.rmtree(path) if recursive else path.rmdir()
            else:
                path.unlink()
            return {"success": True, "path": str(path)}
        
        elif tool_name == "search_files":
            pattern = params.get("*", "")
            file_type = params.get("file_type")
            
            results = []
            for match in path.rglob(pattern):
                if match.is_file():
                    if file_type and not match.suffix.endswith(file_type):
                        continue
                    results.append(str(match.relative_to(path)))
            return results
        
        elif tool_name == "get_file_info":
            stat = path.stat()
            return {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "is_directory": path.is_dir(),
                "is_file": path.is_file(),
                "modified": stat.st_mtime,
                "created": stat.st_ctime
            }
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    def _resolve_path(self, relative_path: str) -> Path:
        """解析路径，确保在允许的目录内"""
        if not relative_path:
            return self.base_path
        
        resolved = (self.base_path / relative_path).resolve()
        
        # 安全检查：确保路径在允许的目录内
        try:
            resolved.relative_to(self.base_path.resolve())
        except ValueError:
            raise ValueError(f"路径不在允许的目录内: {relative_path}")
        
        return resolved
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "filesystem://cwd":
            return str(self.base_path.resolve())
        raise ValueError(f"Unknown resource: {resource.uri}")
