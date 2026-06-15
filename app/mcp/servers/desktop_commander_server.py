"""
Desktop Commander MCP Server
终端命令执行与文件操作工具，支持进程管理、文件读写编辑和搜索
"""

import os
import re
import subprocess
import shutil
import asyncio
import signal
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class DESKTOP_COMMANDERMCPServer(BaseMCPServer):

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.base_path = Path(cfg.get("base_path", ".")).resolve()
        self.allowed_commands: List[str] = cfg.get("allowed_commands", [])
        self.blocked_commands: List[str] = cfg.get("blocked_commands", ["rm -rf /", "mkfs"])
        self._processes: Dict[int, subprocess.Popen] = {}
        super().__init__(config)

    def register_tools(self) -> None:
        tools = [
            ("execute_command", "执行 shell 命令并返回输出", {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"},
                    "timeout_ms": {"type": "integer", "description": "超时时间(毫秒)", "default": 30000},
                },
                "required": ["command"]
            }, ServerCapability.EXECUTE),
            ("read_process_output", "读取运行中进程的输出", {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "进程ID"},
                    "timeout_ms": {"type": "integer", "description": "等待超时(毫秒)", "default": 5000},
                },
                "required": ["pid"]
            }, ServerCapability.READ),
            ("force_terminate", "强制终止进程", {
                "type": "object",
                "properties": {"pid": {"type": "integer", "description": "进程ID"}},
                "required": ["pid"]
            }, ServerCapability.EXECUTE),
            ("list_processes", "列出所有由本服务管理的运行中进程", {
                "type": "object", "properties": {}
            }, ServerCapability.READ),
            ("read_file", "读取文件内容，支持偏移和长度", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "offset": {"type": "integer", "description": "行偏移量（负数从末尾计）", "default": 0},
                    "length": {"type": "integer", "description": "读取行数", "default": 0},
                },
                "required": ["path"]
            }, ServerCapability.READ),
            ("write_file", "写入或追加文件内容", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"},
                    "mode": {"type": "string", "enum": ["rewrite", "append"], "default": "rewrite"},
                },
                "required": ["path", "content"]
            }, ServerCapability.WRITE),
            ("edit_block", "精确替换文件中的文本块", {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "old_string": {"type": "string", "description": "要被替换的文本"},
                    "new_string": {"type": "string", "description": "替换后的文本"},
                },
                "required": ["file_path", "old_string", "new_string"]
            }, ServerCapability.WRITE),
            ("list_directory", "列出目录内容", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "目录路径"},
                    "depth": {"type": "integer", "description": "递归深度", "default": 1},
                },
                "required": ["path"]
            }, ServerCapability.READ),
            ("create_directory", "创建目录（含父目录）", {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "目录路径"}},
                "required": ["path"]
            }, ServerCapability.WRITE),
            ("move_file", "移动或重命名文件/目录", {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "源路径"},
                    "destination": {"type": "string", "description": "目标路径"},
                },
                "required": ["source", "destination"]
            }, ServerCapability.WRITE),
            ("get_file_info", "获取文件元数据", {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "文件路径"}},
                "required": ["path"]
            }, ServerCapability.READ),
            ("search_files", "在目录中搜索文件内容", {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "搜索根目录"},
                    "pattern": {"type": "string", "description": "搜索正则表达式"},
                    "file_pattern": {"type": "string", "description": "文件名过滤（glob）"},
                    "ignore_case": {"type": "boolean", "default": False},
                    "max_results": {"type": "integer", "default": 100},
                },
                "required": ["path", "pattern"]
            }, ServerCapability.READ),
        ]
        for name, desc, schema, cap in tools:
            self._register_tool(MCPTool(name=name, description=desc, input_schema=schema, capability=cap))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="desktop_commander://cwd",
            name="工作目录",
            description="当前工作目录信息"
        ))

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        dispatch = {
            "execute_command": self._execute_command,
            "read_process_output": self._read_process_output,
            "force_terminate": self._force_terminate,
            "list_processes": self._list_processes,
            "read_file": self._read_file,
            "write_file": self._write_file,
            "edit_block": self._edit_block,
            "list_directory": self._list_directory,
            "create_directory": self._create_directory,
            "move_file": self._move_file,
            "get_file_info": self._get_file_info,
            "search_files": self._search_files,
        }
        handler = dispatch.get(tool_name)
        if not handler:
            raise ValueError(f"未知工具: {tool_name}")
        return await handler(params)

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "desktop_commander://cwd":
            return {"path": str(self.base_path), "exists": self.base_path.exists()}
        raise ValueError(f"未知资源: {resource.uri}")

    def _resolve_path(self, path_str: str) -> Path:
        path = Path(path_str)
        if not path.is_absolute():
            path = self.base_path / path
        resolved = path.resolve()
        if not str(resolved).startswith(str(self.base_path)):
            raise PermissionError(f"路径越界: {path_str}")
        return resolved

    async def _execute_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        command = params["command"]
        timeout_ms = params.get("timeout_ms", 30000)

        for blocked in self.blocked_commands:
            if blocked in command:
                return {"error": f"命令被安全策略拦截: {blocked}"}

        try:
            proc = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=str(self.base_path)
            )
            self._processes[proc.pid] = proc
            stdout, stderr = proc.communicate(timeout=timeout_ms / 1000)
            self._processes.pop(proc.pid, None)
            return {
                "exit_code": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
            }
        except subprocess.TimeoutExpired:
            return {"pid": proc.pid, "status": "timeout", "message": f"命令超时({timeout_ms}ms)，使用 read_process_output 继续读取"}
        except Exception as e:
            return {"error": str(e)}

    async def _read_process_output(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pid = params["pid"]
        proc = self._processes.get(pid)
        if not proc:
            return {"error": f"进程 {pid} 不存在或已结束"}
        try:
            stdout = proc.stdout.read().decode("utf-8", errors="replace") if proc.stdout else ""
            stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
            return {"pid": pid, "stdout": stdout, "stderr": stderr, "running": proc.poll() is None}
        except Exception as e:
            return {"error": str(e)}

    async def _force_terminate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pid = params["pid"]
        proc = self._processes.get(pid)
        if proc:
            proc.kill()
            self._processes.pop(pid, None)
            return {"status": "terminated", "pid": pid}
        try:
            os.kill(pid, signal.SIGKILL)
            return {"status": "terminated", "pid": pid}
        except ProcessLookupError:
            return {"error": f"进程 {pid} 不存在"}

    async def _list_processes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "processes": [
                {"pid": pid, "running": proc.poll() is None}
                for pid, proc in self._processes.items()
            ]
        }

    async def _read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.is_file():
            raise FileNotFoundError(f"文件不存在: {params['path']}")
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        offset = params.get("offset", 0)
        length = params.get("length", 0)
        if offset < 0:
            offset = max(0, len(lines) + offset)
        if length > 0:
            lines = lines[offset:offset + length]
        elif offset > 0:
            lines = lines[offset:]
        return {"path": str(path), "content": "\n".join(lines), "total_lines": len(content.splitlines())}

    async def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = params.get("mode", "rewrite")
        if mode == "append":
            with open(path, "a", encoding="utf-8") as f:
                f.write(params["content"])
        else:
            path.write_text(params["content"], encoding="utf-8")
        return {"path": str(path), "mode": mode, "size": path.stat().st_size}

    async def _edit_block(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["file_path"])
        if not path.is_file():
            raise FileNotFoundError(f"文件不存在: {params['file_path']}")
        content = path.read_text(encoding="utf-8")
        old = params["old_string"]
        count = content.count(old)
        if count == 0:
            return {"error": "未找到匹配文本", "searched": old[:100]}
        if count > 1:
            return {"error": f"找到 {count} 处匹配，需要更精确的文本", "matches": count}
        new_content = content.replace(old, params["new_string"], 1)
        path.write_text(new_content, encoding="utf-8")
        return {"path": str(path), "replacements": 1}

    async def _list_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.is_dir():
            raise NotADirectoryError(f"不是目录: {params['path']}")
        entries = []
        for entry in sorted(path.iterdir()):
            entries.append({
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else None,
            })
        return {"path": str(path), "entries": entries, "count": len(entries)}

    async def _create_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        path.mkdir(parents=True, exist_ok=True)
        return {"path": str(path), "created": True}

    async def _move_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        src = self._resolve_path(params["source"])
        dst = self._resolve_path(params["destination"])
        if not src.exists():
            raise FileNotFoundError(f"源不存在: {params['source']}")
        shutil.move(str(src), str(dst))
        return {"source": str(src), "destination": str(dst)}

    async def _get_file_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(params["path"])
        if not path.exists():
            raise FileNotFoundError(f"路径不存在: {params['path']}")
        stat = path.stat()
        return {
            "path": str(path),
            "type": "dir" if path.is_dir() else "file",
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
        }

    async def _search_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        search_path = self._resolve_path(params["path"])
        pattern = re.compile(
            params["pattern"],
            re.IGNORECASE if params.get("ignore_case") else 0
        )
        file_pattern = params.get("file_pattern", "*")
        max_results = params.get("max_results", 100)
        results = []
        for file_path in search_path.rglob(file_pattern):
            if not file_path.is_file():
                continue
            try:
                for line_num, line in enumerate(file_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if pattern.search(line):
                        results.append({
                            "file": str(file_path.relative_to(self.base_path)),
                            "line": line_num,
                            "content": line.strip(),
                        })
                        if len(results) >= max_results:
                            return {"results": results, "truncated": True}
            except (PermissionError, OSError):
                continue
        return {"results": results, "truncated": False, "count": len(results)}
