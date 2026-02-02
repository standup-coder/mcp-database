"""
日历MCP服务器
提供日程管理和节假日查询服务
"""

import asyncio
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

try:
    from mcp import ServerCapabilities, Resource, Tool
    from mcp.server import Server
    from mcp.types import TextContent, ToolCallRequest, ToolCallResponse, ResourceContents
except ImportError:
    class Server:
        def __init__(self, name: str):
            self.name = name
            self.tools = []
            self.resources = []

from ...utils.logger import get_logger
from ...config.settings import settings

logger = get_logger(__name__)


class CalendarEventType(Enum):
    """日历事件类型"""
    WORK = "work"
    PERSONAL = "personal"
    HOLIDAY = "holiday"
    MEETING = "meeting"
    REMINDER = "reminder"


class CalendarMCPServer:
    """日历MCP服务器实现"""
    
    def __init__(self):
        self.server = Server("calendar-mcp-server")
        self.events_storage = {}  # 简化的事件存储
        self._register_tools()
        self._register_resources()
        self._initialize_sample_data()
    
    def _register_tools(self):
        """注册MCP工具"""
        tools = [
            Tool(
                name="get_events",
                description="获取指定时间段内的日程事件",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "开始日期 YYYY-MM-DD"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期 YYYY-MM-DD"
                        },
                        "event_type": {
                            "type": "string",
                            "description": "事件类型过滤",
                            "enum": [et.value for et in CalendarEventType]
                        }
                    }
                }
            ),
            Tool(
                name="add_event",
                description="添加新的日程事件",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "事件标题"
                        },
                        "description": {
                            "type": "string",
                            "description": "事件描述"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "开始时间 ISO格式"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "结束时间 ISO格式"
                        },
                        "event_type": {
                            "type": "string",
                            "description": "事件类型",
                            "enum": [et.value for et in CalendarEventType]
                        },
                        "location": {
                            "type": "string",
                            "description": "地点"
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "参与者邮箱列表"
                        }
                    },
                    "required": ["title", "start_time", "end_time"]
                }
            ),
            Tool(
                name="get_holidays",
                description="获取指定年份的节假日信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份",
                            "default": datetime.now().year
                        },
                        "country": {
                            "type": "string",
                            "description": "国家/地区代码",
                            "default": "CN"
                        }
                    }
                }
            ),
            Tool(
                name="check_availability",
                description="检查时间段的可用性",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_time": {"type": "string"},
                        "end_time": {"type": "string"},
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["start_time", "end_time"]
                }
            )
        ]
        
        for tool in tools:
            self.server.tools.append(tool)
    
    def _register_resources(self):
        """注册MCP资源"""
        resources = [
            Resource(
                uri="calendar://config/event_types",
                name="事件类型说明",
                mimeType="application/json",
                description="支持的日历事件类型及其说明"
            ),
            Resource(
                uri="calendar://config/holiday_rules",
                name="节假日规则",
                mimeType="application/json",
                description="节假日计算规则和例外情况"
            )
        ]
        
        for resource in resources:
            self.server.resources.append(resource)
    
    def _initialize_sample_data(self):
        """初始化示例数据"""
        today = datetime.now()
        
        # 添加示例事件
        sample_events = [
            {
                "id": "evt_001",
                "title": "团队周会",
                "description": "每周团队同步会议",
                "start_time": (today + timedelta(days=1)).replace(hour=10, minute=0).isoformat(),
                "end_time": (today + timedelta(days=1)).replace(hour=11, minute=0).isoformat(),
                "event_type": CalendarEventType.MEETING.value,
                "location": "会议室A",
                "attendees": ["team@example.com"]
            },
            {
                "id": "evt_002",
                "title": "项目评审",
                "description": "季度项目进度评审",
                "start_time": (today + timedelta(days=3)).replace(hour=14, minute=0).isoformat(),
                "end_time": (today + timedelta(days=3)).replace(hour=16, minute=0).isoformat(),
                "event_type": CalendarEventType.WORK.value,
                "location": "线上会议",
                "attendees": ["stakeholders@example.com"]
            }
        ]
        
        for event in sample_events:
            date_key = event["start_time"][:10]  # YYYY-MM-DD
            if date_key not in self.events_storage:
                self.events_storage[date_key] = []
            self.events_storage[date_key].append(event)
    
    async def handle_tool_call(self, request: ToolCallRequest) -> ToolCallResponse:
        """处理工具调用请求"""
        try:
            tool_name = request.name
            arguments = request.arguments or {}
            
            logger.info(f"处理工具调用: {tool_name}", arguments=arguments)
            
            if tool_name == "get_events":
                result = await self._get_events(arguments)
            elif tool_name == "add_event":
                result = await self._add_event(arguments)
            elif tool_name == "get_holidays":
                result = await self._get_holidays(arguments)
            elif tool_name == "check_availability":
                result = await self._check_availability(arguments)
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
    
    async def _get_events(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取日程事件"""
        start_date = args.get("start_date", datetime.now().strftime("%Y-%m-%d"))
        end_date = args.get("end_date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        event_type = args.get("event_type")
        
        events = []
        
        # 简单的时间范围筛选
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date <= end_datetime:
            date_key = current_date.strftime("%Y-%m-%d")
            if date_key in self.events_storage:
                day_events = self.events_storage[date_key]
                if event_type:
                    day_events = [e for e in day_events if e["event_type"] == event_type]
                events.extend(day_events)
            current_date += timedelta(days=1)
        
        result = {
            "events": events,
            "total_count": len(events),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("事件获取完成", result=result)
        return result
    
    async def _add_event(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """添加日程事件"""
        import uuid
        
        event = {
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "title": args["title"],
            "description": args.get("description", ""),
            "start_time": args["start_time"],
            "end_time": args["end_time"],
            "event_type": args.get("event_type", CalendarEventType.PERSONAL.value),
            "location": args.get("location", ""),
            "attendees": args.get("attendees", []),
            "created_at": datetime.now().isoformat()
        }
        
        # 存储事件
        date_key = event["start_time"][:10]
        if date_key not in self.events_storage:
            self.events_storage[date_key] = []
        self.events_storage[date_key].append(event)
        
        result = {
            "status": "success",
            "event_id": event["id"],
            "message": "事件添加成功",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("事件添加完成", result=result)
        return result
    
    async def _get_holidays(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取节假日信息"""
        year = args.get("year", datetime.now().year)
        country = args.get("country", "CN")
        
        # 模拟节假日数据（中国）
        holidays = {
            "CN": {
                year: [
                    {"date": f"{year}-01-01", "name": "元旦", "type": "public"},
                    {"date": f"{year}-02-10", "name": "春节", "type": "public"},
                    {"date": f"{year}-02-11", "name": "春节", "type": "public"},
                    {"date": f"{year}-02-12", "name": "春节", "type": "public"},
                    {"date": f"{year}-04-04", "name": "清明节", "type": "public"},
                    {"date": f"{year}-05-01", "name": "劳动节", "type": "public"},
                    {"date": f"{year}-06-14", "name": "端午节", "type": "public"},
                    {"date": f"{year}-09-21", "name": "中秋节", "type": "public"},
                    {"date": f"{year}-10-01", "name": "国庆节", "type": "public"},
                    {"date": f"{year}-10-02", "name": "国庆节", "type": "public"},
                    {"date": f"{year}-10-03", "name": "国庆节", "type": "public"}
                ]
            }
        }
        
        country_holidays = holidays.get(country, {}).get(year, [])
        
        result = {
            "year": year,
            "country": country,
            "holidays": country_holidays,
            "total_count": len(country_holidays),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("节假日信息获取完成", result=result)
        return result
    
    async def _check_availability(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """检查时间段可用性"""
        start_time = datetime.fromisoformat(args["start_time"])
        end_time = datetime.fromisoformat(args["end_time"])
        attendees = args.get("attendees", [])
        
        # 检查冲突事件
        conflicts = []
        date_key = start_time.strftime("%Y-%m-%d")
        
        if date_key in self.events_storage:
            for event in self.events_storage[date_key]:
                event_start = datetime.fromisoformat(event["start_time"])
                event_end = datetime.fromisoformat(event["end_time"])
                
                # 检查时间冲突
                if (start_time < event_end and end_time > event_start):
                    conflicts.append({
                        "event_id": event["id"],
                        "event_title": event["title"],
                        "conflict_time": {
                            "start": max(start_time, event_start).isoformat(),
                            "end": min(end_time, event_end).isoformat()
                        }
                    })
        
        result = {
            "available": len(conflicts) == 0,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "checked_attendees": attendees,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("可用性检查完成", result=result)
        return result
    
    async def read_resource(self, uri: str) -> ResourceContents:
        """读取资源内容"""
        if uri == "calendar://config/event_types":
            content = {
                "event_types": [
                    {"type": et.value, "description": et.name.lower()}
                    for et in CalendarEventType
                ]
            }
        elif uri == "calendar://config/holiday_rules":
            content = {
                "rules": {
                    "CN": {
                        "fixed_holidays": [
                            {"month": 1, "day": 1, "name": "元旦"},
                            {"month": 5, "day": 1, "name": "劳动节"},
                            {"month": 10, "day": 1, "name": "国庆节"}
                        ],
                        "calculated_holidays": [
                            {"name": "春节", "calculation": "农历正月初一"},
                            {"name": "清明节", "calculation": "农历三月初三"},
                            {"name": "端午节", "calculation": "农历五月初五"},
                            {"name": "中秋节", "calculation": "农历八月十五"}
                        ]
                    }
                }
            }
        else:
            raise ValueError(f"未知资源: {uri}")
        
        return ResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(content, ensure_ascii=False)
        )


async def main():
    """MCP服务器入口点"""
    try:
        server = CalendarMCPServer()
        
        try:
            from mcp.server.stdio import stdio_server
            await stdio_server(lambda: server.server)
        except ImportError:
            print("日历MCP服务器启动 (模拟模式)")
            
    except Exception as e:
        logger.error("日历MCP服务器启动失败", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())