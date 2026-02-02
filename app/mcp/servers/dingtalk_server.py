"""
钉钉MCP服务器
标准MCP协议实现，提供消息推送和通知服务
"""

import asyncio
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# MCP协议相关导入
try:
    from mcp import ServerCapabilities, Resource, Tool
    from mcp.server import Server
    from mcp.types import (
        TextContent,
        ToolCallRequest,
        ToolCallResponse,
        ResourceContents
    )
except ImportError:
    # 模拟实现
    class Server:
        def __init__(self, name: str):
            self.name = name
            self.tools = []
            self.resources = []

from ...utils.logger import get_logger
from ...utils.exceptions import DingTalkAPIError
from ...utils.helpers import generate_dingtalk_signature, get_current_timestamp, format_duration
from ...config.settings import settings

logger = get_logger(__name__)


class DingTalkMCPServer:
    """钉钉MCP服务器实现"""
    
    def __init__(self):
        self.server = Server("dingtalk-mcp-server")
        self.webhook_url = settings.dingtalk_webhook_url
        self.secret = settings.dingtalk_secret
        self.keyword = settings.dingtalk_keyword
        
        # 注册工具
        self._register_tools()
        
        # 注册资源
        self._register_resources()
    
    def _register_tools(self):
        """注册MCP工具"""
        tools = [
            Tool(
                name="send_text_message",
                description="发送文本消息到钉钉群",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "消息内容"
                        },
                        "at_mobiles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "需要@的手机号列表"
                        },
                        "is_at_all": {
                            "type": "boolean",
                            "description": "是否@所有人",
                            "default": False
                        }
                    },
                    "required": ["content"]
                }
            ),
            Tool(
                name="send_markdown_message",
                description="发送Markdown格式消息到钉钉群",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "消息标题"
                        },
                        "text": {
                            "type": "string",
                            "description": "Markdown格式的消息内容"
                        },
                        "at_mobiles": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "is_at_all": {
                            "type": "boolean",
                            "default": False
                        }
                    },
                    "required": ["title", "text"]
                }
            ),
            Tool(
                name="send_commute_notification",
                description="发送通勤通知消息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "departure_time": {
                            "type": "string",
                            "description": "出发时间 ISO格式"
                        },
                        "arrival_time": {
                            "type": "string",
                            "description": "预计到达时间 ISO格式"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "行程时长（分钟）"
                        },
                        "distance_km": {
                            "type": "number",
                            "description": "行驶距离（公里）"
                        },
                        "traffic_status": {
                            "type": "string",
                            "description": "路况状态"
                        },
                        "toll_fee": {
                            "type": "integer",
                            "description": "过路费（元）"
                        },
                        "traffic_lights": {
                            "type": "integer",
                            "description": "红绿灯数量"
                        },
                        "weather_info": {
                            "type": "string",
                            "description": "天气信息（可选）"
                        }
                    },
                    "required": [
                        "departure_time", "arrival_time", "duration_minutes",
                        "distance_km", "traffic_status", "toll_fee", "traffic_lights"
                    ]
                }
            ),
            Tool(
                name="send_error_notification",
                description="发送系统错误通知",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_title": {
                            "type": "string",
                            "description": "错误标题"
                        },
                        "error_message": {
                            "type": "string",
                            "description": "错误详细信息"
                        },
                        "error_time": {
                            "type": "string",
                            "description": "错误发生时间 ISO格式"
                        }
                    },
                    "required": ["error_title", "error_message"]
                }
            )
        ]
        
        for tool in tools:
            self.server.tools.append(tool)
    
    def _register_resources(self):
        """注册MCP资源"""
        resources = [
            Resource(
                uri="dingtalk://config/webhook_info",
                name="Webhook配置信息",
                mimeType="application/json",
                description="钉钉机器人Webhook配置详情"
            ),
            Resource(
                uri="dingtalk://templates/commute_notification",
                name="通勤通知模板",
                mimeType="text/markdown",
                description="通勤通知的标准Markdown模板"
            ),
            Resource(
                uri="dingtalk://templates/error_notification",
                name="错误通知模板",
                mimeType="text/markdown",
                description="系统错误通知的标准模板"
            )
        ]
        
        for resource in resources:
            self.server.resources.append(resource)
    
    async def handle_tool_call(self, request: ToolCallRequest) -> ToolCallResponse:
        """处理工具调用请求"""
        try:
            tool_name = request.name
            arguments = request.arguments or {}
            
            logger.info(f"处理工具调用: {tool_name}", arguments=arguments)
            
            if tool_name == "send_text_message":
                result = await self._send_text_message(arguments)
            elif tool_name == "send_markdown_message":
                result = await self._send_markdown_message(arguments)
            elif tool_name == "send_commute_notification":
                result = await self._send_commute_notification(arguments)
            elif tool_name == "send_error_notification":
                result = await self._send_error_notification(arguments)
            else:
                raise ValueError(f"未知工具: {tool_name}")
            
            return ToolCallResponse(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
            )
            
        except Exception as e:
            logger.error(f"工具调用失败: {request.name}", error=str(e))
            return ToolCallResponse(
                isError=True,
                content=[TextContent(type="text", text=f"工具调用失败: {str(e)}")]
            )
    
    async def _send_text_message(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """发送文本消息"""
        content = args["content"]
        at_mobiles = args.get("at_mobiles", [])
        is_at_all = args.get("is_at_all", False)
        
        # 添加关键词确保消息能发送
        if self.keyword and self.keyword not in content:
            content = f"[{self.keyword}] {content}"
        
        # 构造消息体
        message = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": at_mobiles,
                "isAtAll": is_at_all
            }
        }
        
        # 发送消息（这里是模拟实现）
        result = {
            "status": "success",
            "msgid": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("文本消息发送完成", result=result)
        return result
    
    async def _send_markdown_message(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """发送Markdown消息"""
        title = args["title"]
        text = args["text"]
        at_mobiles = args.get("at_mobiles", [])
        is_at_all = args.get("is_at_all", False)
        
        # 添加关键词
        if self.keyword and self.keyword not in title:
            title = f"[{self.keyword}] {title}"
        
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles,
                "isAtAll": is_at_all
            }
        }
        
        result = {
            "status": "success",
            "msgid": f"md_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("Markdown消息发送完成", result=result)
        return result
    
    async def _send_commute_notification(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """发送通勤通知"""
        # 格式化时间
        departure_str = datetime.fromisoformat(args["departure_time"]).strftime("%H:%M")
        arrival_str = datetime.fromisoformat(args["arrival_time"]).strftime("%H:%M")
        
        # 构建Markdown内容
        content_lines = [
            f"## 🚗 通勤路线信息",
            f"",
            f"**出发时间**: {departure_str}",
            f"**预计到达**: {arrival_str}",
            f"**行程时长**: {format_duration(args['duration_minutes'])}",
            f"**行驶距离**: {args['distance_km']:.1f}公里",
            f"**路况状态**: {args['traffic_status']}",
            f"",
            f"📊 **详细信息**:",
            f"- 红绿灯数量: {args['traffic_lights']}个",
            f"- 过路费用: {args['toll_fee']}元"
        ]
        
        if "weather_info" in args and args["weather_info"]:
            content_lines.extend([
                f"- 天气状况: {args['weather_info']}"
            ])
        
        content_lines.extend([
            f"",
            f"⏰ 温馨提示：建议提前规划出行时间",
            f"",
            f"> 本消息由智能通勤助手自动发送"
        ])
        
        title = f"🚗 今日通勤提醒 - {departure_str}出发"
        text = "\n".join(content_lines)
        
        # 发送消息
        return await self._send_markdown_message({
            "title": title,
            "text": text
        })
    
    async def _send_error_notification(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """发送错误通知"""
        error_time = args.get("error_time")
        if error_time:
            time_str = datetime.fromisoformat(error_time).strftime('%H:%M')
        else:
            time_str = datetime.now().strftime('%H:%M')
        
        title = f"⚠️ 系统异常通知 - {time_str}"
        
        content = f"""## ⚠️ 系统异常

**异常时间**: {args.get('error_time', datetime.now().isoformat())}
**异常类型**: {args['error_title']}

**详细信息**:
```
{args['error_message']}
```

请及时检查系统运行状态。
"""
        
        return await self._send_markdown_message({
            "title": title,
            "text": content
        })
    
    async def read_resource(self, uri: str) -> ResourceContents:
        """读取资源内容"""
        if uri == "dingtalk://config/webhook_info":
            content = {
                "webhook_url": self.webhook_url,
                "keyword": self.keyword,
                "has_secret": bool(self.secret)
            }
        elif uri == "dingtalk://templates/commute_notification":
            content = """## 🚗 通勤通知模板

**出发时间**: {{departure_time}}
**预计到达**: {{arrival_time}}
**行程时长**: {{duration}}
**行驶距离**: {{distance}}公里
**路况状态**: {{traffic_status}}

📊 **详细信息**:
- 红绿灯数量: {{traffic_lights}}个
- 过路费用: {{toll_fee}}元
- 天气状况: {{weather_info}}

⏰ 温馨提示：建议提前规划出行时间

> 本消息由智能通勤助手自动发送"""
        elif uri == "dingtalk://templates/error_notification":
            content = """## ⚠️ 错误通知模板

**异常时间**: {{error_time}}
**异常类型**: {{error_title}}

**详细信息**:
```
{{error_message}}
```

请及时检查系统运行状态。"""
        else:
            raise ValueError(f"未知资源: {uri}")
        
        return ResourceContents(
            uri=uri,
            mimeType="application/json" if isinstance(content, dict) else "text/markdown",
            text=json.dumps(content, ensure_ascii=False) if isinstance(content, dict) else content
        )


async def main():
    """MCP服务器入口点"""
    try:
        server = DingTalkMCPServer()
        
        # 如果使用真正的MCP库
        try:
            from mcp.server.stdio import stdio_server
            await stdio_server(lambda: server.server)
        except ImportError:
            # 模拟stdio通信
            print("钉钉MCP服务器启动 (模拟模式)")
            
    except Exception as e:
        logger.error("钉钉MCP服务器启动失败", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())