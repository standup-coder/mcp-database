"""
高德地图MCP服务器
标准MCP协议实现，提供路线规划和路况查询服务
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
    # 如果没有安装mcp库，使用模拟实现
    class Server:
        def __init__(self, name: str):
            self.name = name
            self.tools = []
            self.resources = []
        
        def list_tools(self):
            return self.tools
        
        def list_resources(self):
            return self.resources

from ...utils.logger import get_logger
from ...utils.exceptions import AMAPAPIError
from ...utils.helpers import build_amap_request_params, convert_speed_to_chinese
from ...config.settings import settings

logger = get_logger(__name__)


class AMAPMCPServer:
    """高德地图MCP服务器实现"""
    
    def __init__(self):
        self.server = Server("amap-mcp-server")
        self.api_key = settings.amap_api_key
        self.origin = settings.amap_origin
        self.destination = settings.amap_destination
        self.strategy = settings.amap_strategy
        
        # 注册工具
        self._register_tools()
        
        # 注册资源
        self._register_resources()
    
    def _register_tools(self):
        """注册MCP工具"""
        tools = [
            Tool(
                name="calculate_route",
                description="计算两点间的最优路线",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "出发地坐标，格式：经度,纬度"
                        },
                        "destination": {
                            "type": "string", 
                            "description": "目的地坐标，格式：经度,纬度"
                        },
                        "strategy": {
                            "type": "integer",
                            "description": "路线策略：0-速度优先，1-费用优先，2-距离优先",
                            "default": 0
                        }
                    }
                }
            ),
            Tool(
                name="get_traffic_condition",
                description="获取指定路线的实时路况",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "出发地坐标"
                        },
                        "destination": {
                            "type": "string",
                            "description": "目的地坐标"
                        }
                    }
                }
            ),
            Tool(
                name="batch_calculate_routes",
                description="批量计算多条路线",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "routes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "origin": {"type": "string"},
                                    "destination": {"type": "string"}
                                },
                                "required": ["origin", "destination"]
                            }
                        }
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
                uri="amap://config/default_route",
                name="默认通勤路线",
                mimeType="application/json",
                description="预设的通勤路线配置"
            ),
            Resource(
                uri="amap://config/strategies",
                name="路线策略说明",
                mimeType="text/plain",
                description="不同路线策略的详细说明"
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
            
            if tool_name == "calculate_route":
                result = await self._calculate_route(arguments)
            elif tool_name == "get_traffic_condition":
                result = await self._get_traffic_condition(arguments)
            elif tool_name == "batch_calculate_routes":
                result = await self._batch_calculate_routes(arguments)
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
    
    async def _calculate_route(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """计算路线"""
        origin = args.get("origin", self.origin)
        destination = args.get("destination", self.destination)
        strategy = args.get("strategy", self.strategy)
        
        # 构建请求参数
        params = build_amap_request_params(origin, destination, self.api_key, strategy)
        
        # 这里应该是实际的API调用
        # 模拟响应数据
        route_data = {
            "distance": 15000,  # 15公里
            "duration": 1800,   # 30分钟
            "traffic_lights": 8,
            "strategy": "速度优先",
            "tolls": 0,
            "toll_distance": 0,
            "steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("路线计算完成", route_data=route_data)
        return route_data
    
    async def _get_traffic_condition(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取路况"""
        origin = args.get("origin", self.origin)
        destination = args.get("destination", self.destination)
        
        # 获取路线信息
        route_info = await self._calculate_route({
            "origin": origin,
            "destination": destination
        })
        
        # 计算平均速度
        distance_km = route_info["distance"] / 1000
        duration_hours = route_info["duration"] / 3600
        avg_speed = distance_km / duration_hours if duration_hours > 0 else 0
        
        # 转换路况描述
        congestion_level = convert_speed_to_chinese(avg_speed)
        
        traffic_data = {
            "status": "success",
            "avg_speed": round(avg_speed, 1),
            "congestion_level": congestion_level,
            "description": f"平均速度{avg_speed:.1f}km/h",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug("路况获取完成", traffic_data=traffic_data)
        return traffic_data
    
    async def _batch_calculate_routes(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """批量计算路线"""
        routes = args.get("routes", [])
        results = []
        
        for i, route in enumerate(routes):
            try:
                result = await self._calculate_route(route)
                result["index"] = i
                results.append(result)
            except Exception as e:
                results.append({
                    "index": i,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "results": results,
            "total": len(routes),
            "success_count": len([r for r in results if "error" not in r]),
            "timestamp": datetime.now().isoformat()
        }
    
    async def read_resource(self, uri: str) -> ResourceContents:
        """读取资源内容"""
        if uri == "amap://config/default_route":
            content = {
                "origin": self.origin,
                "destination": self.destination,
                "strategy": self.strategy
            }
        elif uri == "amap://config/strategies":
            content = """
路线策略说明：
0 - 速度优先：选择通行速度最快的路线
1 - 费用优先：选择过路费最少的路线  
2 - 距离优先：选择距离最短的路线
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
        server = AMAPMCPServer()
        
        # 如果使用真正的MCP库
        try:
            from mcp.server.stdio import stdio_server
            await stdio_server(lambda: server.server)
        except ImportError:
            # 模拟stdio通信
            print("MCP服务器启动 (模拟模式)")
            # 这里可以实现简单的stdin/stdout通信
            
    except Exception as e:
        logger.error("MCP服务器启动失败", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())