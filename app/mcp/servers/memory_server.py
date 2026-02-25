"""
Memory MCP服务器
提供知识图谱/持久化记忆功能
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class MemoryMCPServer(BaseMCPServer):
    """Memory MCP服务器 (知识图谱)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.storage_path = Path(config.get("storage_path", "./memory_data")) if config else Path("./memory_data")
        self.storage_path.mkdir(exist_ok=True)
        super().__init__(config)
    
    def register_tools(self):
        """注册记忆操作工具"""
        self._register_tool(MCPTool(
            name="store",
            description="存储记忆",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "记忆键"},
                    "value": {"type": "string", "description": "记忆内容"},
                    "tags": {"type": "array", "description": "标签"}
                },
                "required": ["key", "value"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="retrieve",
            description="检索记忆",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "记忆键"}
                },
                "required": ["key"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="search",
            description="搜索记忆",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "tags": {"type": "array", "description": "标签过滤"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="list_keys",
            description="列出所有记忆键",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "模式匹配"}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="delete",
            description="删除记忆",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "记忆键"}
                },
                "required": ["key"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="add_entity",
            description="添加实体到知识图谱",
            input_schema={
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "description": "实体名"},
                    "entity_type": {"type": "string", "description": "实体类型"},
                    "properties": {"type": "object", "description": "属性"}
                },
                "required": ["entity", "entity_type"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="add_relation",
            description="添加关系",
            input_schema={
                "type": "object",
                "properties": {
                    "from_entity": {"type": "string", "description": "源实体"},
                    "relation": {"type": "string", "description": "关系类型"},
                    "to_entity": {"type": "string", "description": "目标实体"}
                },
                "required": ["from_entity", "relation", "to_entity"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="query_graph",
            description="查询知识图谱",
            input_schema={
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "description": "实体名"},
                    "depth": {"type": "integer", "default": 1}
                },
                "required": ["entity"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="export",
            description="导出所有记忆",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册资源"""
        self._register_resource(MCPResource(
            uri="memory://keys",
            name="all_keys",
            description="所有记忆键"
        ))
        self._register_resource(MCPResource(
            uri="memory://graph",
            name="knowledge_graph",
            description="知识图谱"
        ))
    
    def _get_memory_file(self, key: str) -> Path:
        """获取记忆文件路径"""
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self.storage_path / f"{safe_key}.json"
    
    def _get_graph_file(self) -> Path:
        """获取知识图谱文件"""
        return self.storage_path / "graph.json"
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行记忆操作"""
        
        if tool_name == "store":
            key = params.get("key", "")
            value = params.get("value", "")
            tags = params.get("tags", [])
            
            memory = {
                "key": key,
                "value": value,
                "tags": tags,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            file_path = self._get_memory_file(key)
            file_path.write_text(json.dumps(memory, ensure_ascii=False, indent=2))
            
            return {"stored": key}
        
        elif tool_name == "retrieve":
            key = params.get("key", "")
            file_path = self._get_memory_file(key)
            
            if not file_path.exists():
                return {"error": "Memory not found", "key": key}
            
            content = json.loads(file_path.read_text())
            return content
        
        elif tool_name == "search":
            query = params.get("query", "").lower()
            tags = params.get("tags", [])
            limit = params.get("limit", 10)
            
            results = []
            for file_path in self.storage_path.glob("*.json"):
                try:
                    memory = json.loads(file_path.read_text())
                    
                    match = query in memory.get("value", "").lower() or query in memory.get("key", "").lower()
                    
                    if tags:
                        tag_match = any(tag in memory.get("tags", []) for tag in tags)
                    else:
                        tag_match = True
                    
                    if match and tag_match:
                        results.append(memory)
                except:
                    continue
            
            return results[:limit]
        
        elif tool_name == "list_keys":
            pattern = params.get("pattern", "*")
            keys = [f.stem for f in self.storage_path.glob(f"{pattern}.json")]
            return {"keys": keys}
        
        elif tool_name == "delete":
            key = params.get("key", "")
            file_path = self._get_memory_file(key)
            
            if file_path.exists():
                file_path.unlink()
                return {"deleted": key}
            return {"error": "Memory not found"}
        
        elif tool_name == "add_entity":
            graph_file = self._get_graph_file()
            graph = {"entities": [], "relations": []}
            
            if graph_file.exists():
                graph = json.loads(graph_file.read_text())
            
            entity = {
                "name": params.get("entity", ""),
                "type": params.get("entity_type", ""),
                "properties": params.get("properties", {}),
                "created_at": datetime.now().isoformat()
            }
            
            graph["entities"].append(entity)
            graph_file.write_text(json.dumps(graph, ensure_ascii=False, indent=2))
            
            return {"added": entity["name"]}
        
        elif tool_name == "add_relation":
            graph_file = self._get_graph_file()
            graph = {"entities": [], "relations": []}
            
            if graph_file.exists():
                graph = json.loads(graph_file.read_text())
            
            relation = {
                "from": params.get("from_entity", ""),
                "relation": params.get("relation", ""),
                "to": params.get("to_entity", ""),
                "created_at": datetime.now().isoformat()
            }
            
            graph["relations"].append(relation)
            graph_file.write_text(json.dumps(graph, ensure_ascii=False, indent=2))
            
            return {"added": relation}
        
        elif tool_name == "query_graph":
            entity = params.get("entity", "")
            depth = params.get("depth", 1)
            
            graph_file = self._get_graph_file()
            if not graph_file.exists():
                return {"entities": [], "relations": []}
            
            graph = json.loads(graph_file.read_text())
            
            result = {"entity": entity, "relations": [], "connected": []}
            
            for rel in graph.get("relations", []):
                if rel.get("from") == entity:
                    result["relations"].append(rel)
                    result["connected"].append(rel.get("to"))
                elif rel.get("to") == entity:
                    result["relations"].append(rel)
                    result["connected"].append(rel.get("from"))
            
            return result
        
        elif tool_name == "export":
            memories = []
            for file_path in self.storage_path.glob("*.json"):
                if file_path.name != "graph.json":
                    try:
                        memories.append(json.loads(file_path.read_text()))
                    except:
                        continue
            
            graph_file = self._get_graph_file()
            graph = json.loads(graph_file.read_text()) if graph_file.exists() else {"entities": [], "relations": []}
            
            return {"memories": memories, "graph": graph}
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "memory://keys":
            keys = [f.stem for f in self.storage_path.glob("*.json") if f.stem != "graph"]
            return {"keys": keys}
        elif resource.uri == "memory://graph":
            graph_file = self._get_graph_file()
            if graph_file.exists():
                return json.loads(graph_file.read_text())
            return {"entities": [], "relations": []}
        raise ValueError(f"Unknown resource: {resource.uri}")
