"""
数据库MCP服务器
支持MySQL、PostgreSQL、SQLite、Redis等数据库
"""

import json
from typing import Any, Dict, List, Optional
from enum import Enum

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class DatabaseType(Enum):
    """数据库类型"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    REDIS = "redis"
    MONGODB = "mongodb"


class DatabaseMCPServer(BaseMCPServer):
    """数据库MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.db_type = DatabaseType(config.get("db_type", "sqlite") if config else "sqlite")
        self.connection_config = config or {}
        self._connection = None
        super().__init__(config)
    
    def register_tools(self):
        """注册数据库操作工具"""
        self._register_tool(MCPTool(
            name="execute",
            description="执行SQL查询",
            input_schema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL语句"},
                    "params": {"type": "array", "description": "查询参数"}
                },
                "required": ["sql"]
            },
            capability=ServerCapability.EXECUTE
        ))
        
        self._register_tool(MCPTool(
            name="query",
            description="执行查询并返回结果",
            input_schema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SELECT语句"},
                    "params": {"type": "array", "description": "查询参数"},
                    "limit": {"type": "integer", "default": 100}
                },
                "required": ["sql"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="list_tables",
            description="列出所有表",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="describe_table",
            description="获取表结构",
            input_schema={
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "表名"}
                },
                "required": ["table"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_keys",
            description="获取Redis keys",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "default": "*"},
                    "count": {"type": "integer", "default": 100}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="set_value",
            description="设置值（Redis）",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "键"},
                    "value": {"type": "string", "description": "值"},
                    "ttl": {"type": "integer", "description": "过期时间(秒)"}
                },
                "required": ["key", "value"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="get_value",
            description="获取值（Redis）",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "键"}
                },
                "required": ["key"]
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册数据库资源"""
        self._register_resource(MCPResource(
            uri="db://tables",
            name="table_list",
            description="数据库表列表"
        ))
    
    def _get_connection(self):
        """获取数据库连接"""
        if self._connection is not None:
            return self._connection
        
        if self.db_type == DatabaseType.SQLITE:
            import sqlite3
            db_path = self.connection_config.get("path", "database.db")
            self._connection = sqlite3.connect(db_path)
        
        elif self.db_type == DatabaseType.MYSQL:
            import pymysql
            self._connection = pymysql.connect(
                host=self.connection_config.get("host", "localhost"),
                port=self.connection_config.get("port", 3306),
                user=self.connection_config.get("user", "root"),
                password=self.connection_config.get("password", ""),
                database=self.connection_config.get("database", "")
            )
        
        elif self.db_type == DatabaseType.POSTGRESQL:
            import psycopg2
            self._connection = psycopg2.connect(
                host=self.connection_config.get("host", "localhost"),
                port=self.connection_config.get("port", 5432),
                user=self.connection_config.get("user", "postgres"),
                password=self.connection_config.get("password", ""),
                database=self.connection_config.get("database", "")
            )
        
        elif self.db_type == DatabaseType.REDIS:
            import redis
            self._connection = redis.Redis(
                host=self.connection_config.get("host", "localhost"),
                port=self.connection_config.get("port", 6379),
                db=self.connection_config.get("db", 0),
                password=self.connection_config.get("password")
            )
        
        return self._connection
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行数据库操作"""
        sql = params.get("sql", "")
        query_params = params.get("params", [])
        
        if self.db_type == DatabaseType.REDIS:
            return await self._execute_redis(tool_name, params)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if tool_name == "execute":
                cursor.execute(sql, query_params)
                conn.commit()
                return {"affected_rows": cursor.rowcount}
            
            elif tool_name == "query":
                limit = params.get("limit", 100)
                cursor.execute(sql, query_params)
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                return {
                    "columns": columns,
                    "rows": rows[:limit],
                    "total": len(rows)
                }
            
            elif tool_name == "list_tables":
                if self.db_type == DatabaseType.SQLITE:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                elif self.db_type == DatabaseType.MYSQL:
                    cursor.execute("SHOW TABLES")
                elif self.db_type == DatabaseType.POSTGRESQL:
                    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                return [row[0] for row in cursor.fetchall()]
            
            elif tool_name == "describe_table":
                table = params.get("table", "")
                if self.db_type == DatabaseType.SQLITE:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    return [{"name": c[1], "type": c[2], "nullable": not c[3], "default": c[4]} for c in columns]
                elif self.db_type == DatabaseType.MYSQL:
                    cursor.execute(f"DESCRIBE {table}")
                    return [{"Field": row[0], "Type": row[1], "Null": row[2], "Key": row[3], "Default": row[4]} for row in cursor.fetchall()]
                elif self.db_type == DatabaseType.POSTGRESQL:
                    cursor.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'")
                    return [{"column": row[0], "type": row[1], "nullable": row[2]} for row in cursor.fetchall()]
        
        finally:
            cursor.close()
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_redis(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行Redis操作"""
        r = self._get_connection()
        
        if tool_name == "get_keys":
            pattern = params.get("pattern", "*")
            count = params.get("count", 100)
            return r.keys(pattern)[:count]
        
        elif tool_name == "set_value":
            key = params.get("key", "")
            value = params.get("value", "")
            ttl = params.get("ttl")
            if ttl:
                r.setex(key, ttl, value)
            else:
                r.set(key, value)
            return {"success": True}
        
        elif tool_name == "get_value":
            key = params.get("key", "")
            value = r.get(key)
            return value.decode() if value else None
        
        raise ValueError(f"Unknown Redis tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "db://tables":
            if self.db_type == DatabaseType.REDIS:
                return self._get_connection().keys("*")
            return await self.execute_tool("list_tables", {})
        raise ValueError(f"Unknown resource: {resource.uri}")
