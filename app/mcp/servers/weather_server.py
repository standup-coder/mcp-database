"""
天气MCP服务器
提供天气查询和预报服务
"""

import asyncio
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

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


class WeatherMCPServer:
    """天气MCP服务器实现"""
    
    def __init__(self):
        self.server = Server("weather-mcp-server")
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """注册MCP工具"""
        tools = [
            Tool(
                name="get_current_weather",
                description="获取指定城市的当前天气",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        },
                        "coordinates": {
                            "type": "string",
                            "description": "坐标，格式：经度,纬度"
                        }
                    }
                }
            ),
            Tool(
                name="get_weather_forecast",
                description="获取未来几天的天气预报",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "days": {
                            "type": "integer",
                            "description": "预报天数（1-7天）",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 7
                        }
                    }
                }
            ),
            Tool(
                name="get_air_quality",
                description="获取空气质量指数",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "coordinates": {"type": "string"}
                    }
                }
            )
        ]
        
        for tool in tools:
            self.server.tools.append(tool)
    
    def _register_resources(self):
        """注册MCP资源"""
        resources = [
            Resource(
                uri="weather://config/supported_cities",
                name="支持的城市列表",
                mimeType="application/json",
                description="当前支持天气查询的城市列表"
            ),
            Resource(
                uri="weather://config/weather_codes",
                name="天气代码说明",
                mimeType="text/plain",
                description="天气状况代码对照表"
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
            
            if tool_name == "get_current_weather":
                result = await self._get_current_weather(arguments)
            elif tool_name == "get_weather_forecast":
                result = await self._get_weather_forecast(arguments)
            elif tool_name == "get_air_quality":
                result = await self._get_air_quality(arguments)
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
    
    async def _get_current_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取当前天气"""
        city = args.get("city", "北京")
        
        # 模拟天气数据
        weather_data = {
            "city": city,
            "temperature": 22,  # 摄氏度
            "humidity": 65,     # 湿度百分比
            "wind_speed": 3.5,  # 风速 m/s
            "wind_direction": "东北风",
            "pressure": 1013,   # 气压 hPa
            "visibility": 10,   # 能见度 km
            "weather_condition": "晴",
            "weather_code": 0,
            "feels_like": 24,
            "uv_index": 5,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("当前天气获取完成", weather_data=weather_data)
        return weather_data
    
    async def _get_weather_forecast(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取天气预报"""
        city = args.get("city", "北京")
        days = min(args.get("days", 3), 7)
        
        forecast_data = []
        base_temp = 22
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            # 模拟温度变化
            temp_variation = (-2 + i) if i < days//2 else (days - i - 1)
            high_temp = base_temp + temp_variation + 5
            low_temp = base_temp + temp_variation - 5
            
            day_data = {
                "date": date,
                "high_temperature": high_temp,
                "low_temperature": low_temp,
                "weather_condition": "晴转多云" if i % 2 == 0 else "多云",
                "precipitation_probability": 10 + i * 5,  # 降水概率
                "wind_speed": 2.0 + i * 0.5
            }
            forecast_data.append(day_data)
        
        result = {
            "city": city,
            "forecast_days": days,
            "forecasts": forecast_data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("天气预报获取完成", result=result)
        return result
    
    async def _get_air_quality(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取空气质量"""
        city = args.get("city", "北京")
        
        # 模拟空气质量数据
        aqi_data = {
            "city": city,
            "aqi": 85,          # AQI指数
            "level": "良",       # 空气质量等级
            "pm2_5": 62,        # PM2.5浓度
            "pm10": 88,         # PM10浓度
            "o3": 120,          # 臭氧浓度
            "no2": 35,          # 二氧化氮浓度
            "so2": 12,          # 二氧化硫浓度
            "co": 0.8,          # 一氧化碳浓度
            "primary_pollutant": "PM2.5",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("空气质量获取完成", aqi_data=aqi_data)
        return aqi_data
    
    async def read_resource(self, uri: str) -> ResourceContents:
        """读取资源内容"""
        if uri == "weather://config/supported_cities":
            content = {
                "cities": [
                    "北京", "上海", "广州", "深圳", "杭州", "南京", "成都",
                    "武汉", "西安", "重庆", "天津", "苏州", "长沙"
                ],
                "last_updated": datetime.now().isoformat()
            }
        elif uri == "weather://config/weather_codes":
            content = """
天气代码说明：
0 - 晴
1 - 多云
2 - 阴
3 - 阵雨
4 - 雷阵雨
5 - 雨夹雪
6 - 小雨
7 - 中雨
8 - 大雨
9 - 暴雨
            """.strip()
        else:
            raise ValueError(f"未知资源: {uri}")
        
        return ResourceContents(
            uri=uri,
            mimeType="application/json" if isinstance(content, dict) else "text/plain",
            text=json.dumps(content, ensure_ascii=False) if isinstance(content, dict) else content
        )


async def main():
    """MCP服务器入口点"""
    try:
        server = WeatherMCPServer()
        
        try:
            from mcp.server.stdio import stdio_server
            await stdio_server(lambda: server.server)
        except ImportError:
            print("天气MCP服务器启动 (模拟模式)")
            
    except Exception as e:
        logger.error("天气MCP服务器启动失败", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())