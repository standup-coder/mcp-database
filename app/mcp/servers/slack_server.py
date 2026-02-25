"""
Slack MCP服务器
提供Slack API操作功能
"""

import os
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class SlackMCPServer(BaseMCPServer):
    """Slack MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.token = config.get("token", os.environ.get("SLACK_BOT_TOKEN", ""))
        self.signing_secret = config.get("signing_secret", os.environ.get("SLACK_SIGNING_SECRET", ""))
        super().__init__(config)
    
    def register_tools(self):
        """注册Slack操作工具"""
        self._register_tool(MCPTool(
            name="post_message",
            description="发送消息到Slack频道",
            input_schema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "频道ID"},
                    "text": {"type": "string", "description": "消息内容"},
                    "blocks": {"type": "array", "description": "Block Kit UI"}
                },
                "required": ["channel", "text"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="post_markdown",
            description="发送Markdown格式消息",
            input_schema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "频道ID"},
                    "title": {"type": "string", "description": "标题"},
                    "text": {"type": "string", "description": "Markdown内容"}
                },
                "required": ["channel", "text"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="list_channels",
            description="列出Slack频道",
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_channel_info",
            description="获取频道信息",
            input_schema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "频道ID"}
                },
                "required": ["channel"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="list_messages",
            description="获取频道消息历史",
            input_schema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "频道ID"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["channel"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="create_channel",
            description="创建Slack频道",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "频道名称"},
                    "is_private": {"type": "boolean", "default": False}
                },
                "required": ["name"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="add_reaction",
            description="添加emoji反应",
            input_schema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "频道ID"},
                    "timestamp": {"type": "string", "description": "消息时间戳"},
                    "emoji": {"type": "string", "description": "emoji名称"}
                },
                "required": ["channel", "timestamp", "emoji"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="list_users",
            description="列出工作区用户",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册Slack资源"""
        self._register_resource(MCPResource(
            uri="slack://channels",
            name="channel_list",
            description="频道列表"
        ))
        self._register_resource(MCPResource(
            uri="slack://users",
            name="user_list",
            description="用户列表"
        ))
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """发送Slack API请求"""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        url = f"https://slack.com/api/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            result = response.json()
            if not result.get("ok"):
                raise ValueError(f"Slack API error: {result.get('error', 'Unknown error')}")
            return result
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行Slack操作"""
        channel = params.get("channel", "")
        text = params.get("text", "")
        
        if tool_name == "post_message":
            return await self._make_request("POST", "chat.postMessage", {
                "channel": channel,
                "text": text,
                "blocks": params.get("blocks")
            })
        
        elif tool_name == "post_markdown":
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": params.get("title", "")}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text}
                }
            ]
            return await self._make_request("POST", "chat.postMessage", {
                "channel": channel,
                "blocks": blocks
            })
        
        elif tool_name == "list_channels":
            limit = params.get("limit", 100)
            return await self._make_request("GET", "conversations.list", {"limit": limit})
        
        elif tool_name == "get_channel_info":
            return await self._make_request("GET", "conversations.info", {"channel": channel})
        
        elif tool_name == "list_messages":
            return await self._make_request("GET", "conversations.history", {
                "channel": channel,
                "limit": params.get("limit", 10)
            })
        
        elif tool_name == "create_channel":
            name = params.get("name", "")
            is_private = params.get("is_private", False)
            return await self._make_request("POST", "conversations.create", {
                "name": name,
                "is_private": is_private
            })
        
        elif tool_name == "add_reaction":
            return await self._make_request("POST", "reactions.add", {
                "channel": channel,
                "timestamp": params.get("timestamp", ""),
                "name": params.get("emoji", "")
            })
        
        elif tool_name == "list_users":
            return await self._make_request("GET", "users.list", {})
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "slack://channels":
            return await self._make_request("GET", "conversations.list", {"limit": 100})
        elif resource.uri == "slack://users":
            return await self._make_request("GET", "users.list", {})
        raise ValueError(f"Unknown resource: {resource.uri}")
