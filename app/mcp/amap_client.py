"""
高德地图MCP客户端
实现路线查询和时长计算功能
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

from ..config.settings import settings
from ..utils.logger import get_logger
from ..utils.exceptions import AMAPAPIError, RouteCalculationError
from ..utils.error_handler import retry, NETWORK_RETRY_CONFIG
from ..utils.helpers import build_amap_request_params, convert_speed_to_chinese

logger = get_logger(__name__)


class RouteInfo(BaseModel):
    """路线信息模型"""
    distance: int  # 距离（米）
    duration: int  # 时长（秒）
    traffic_lights: int  # 红绿灯数量
    strategy: str  # 路线策略
    tolls: int  # 过路费（元）
    toll_distance: int  # 收费路段距离（米）
    steps: List[Dict[str, Any]]  # 路线步骤详情


class TrafficCondition(BaseModel):
    """路况信息模型"""
    status: str  # 路况状态
    description: str  # 路况描述
    speed: float  # 平均速度（km/h）
    congestion_level: str  # 拥堵等级


class AMAPClient:
    """高德地图API客户端"""
    
    def __init__(self):
        self.api_key = settings.amap_api_key
        self.base_url = "https://restapi.amap.com/v3"
        self.timeout = 10.0
        self.client = None
    
    async def __aenter__(self):
        """异步上下文管理器进入"""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.client:
            await self.client.aclose()
    
    @retry(config=NETWORK_RETRY_CONFIG)
    async def _make_request(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            Dict: API响应数据
            
        Raises:
            AMAPAPIError: API请求失败
        """
        if not self.client:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查API响应状态
            if data.get('status') != '1':
                error_msg = data.get('info', '未知错误')
                raise AMAPAPIError(f"高德API调用失败: {error_msg}")
            
            logger.debug(f"高德API请求成功: {endpoint}", response_data=str(data)[:200])
            return data
            
        except httpx.RequestError as e:
            logger.error(f"高德API网络请求失败: {str(e)}")
            raise AMAPAPIError(f"网络请求失败: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"高德API HTTP错误: {e.response.status_code}")
            raise AMAPAPIError(
                f"HTTP错误: {e.response.status_code}", 
                status_code=e.response.status_code
            )
    
    async def calculate_route(
        self, 
        origin: str = None, 
        destination: str = None,
        strategy: int = None
    ) -> RouteInfo:
        """
        计算路线信息
        
        Args:
            origin: 出发地坐标 "经度,纬度"
            destination: 目的地坐标 "经度,纬度"
            strategy: 路线策略
            
        Returns:
            RouteInfo: 路线信息
            
        Raises:
            RouteCalculationError: 路线计算失败
        """
        # 使用配置中的默认值
        origin = origin or settings.amap_origin
        destination = destination or settings.amap_destination
        strategy = strategy or settings.amap_strategy
        
        logger.info(
            "开始计算路线",
            origin=origin,
            destination=destination,
            strategy=strategy
        )
        
        try:
            params = build_amap_request_params(origin, destination, self.api_key, strategy)
            
            data = await self._make_request('direction/driving', params)
            
            # 解析路线信息
            route = self._parse_route_data(data)
            
            logger.info(
                "路线计算完成",
                distance=f"{route.distance}米",
                duration=f"{route.duration}秒",
                tolls=f"{route.tolls}元"
            )
            
            return route
            
        except AMAPAPIError as e:
            logger.error("路线计算API调用失败", error=str(e))
            raise RouteCalculationError(f"路线计算失败: {str(e)}")
        except Exception as e:
            logger.error("路线计算过程异常", error=str(e))
            raise RouteCalculationError(f"路线计算异常: {str(e)}")
    
    def _parse_route_data(self, data: Dict[str, Any]) -> RouteInfo:
        """
        解析路线数据
        
        Args:
            data: API响应数据
            
        Returns:
            RouteInfo: 解析后的路线信息
        """
        try:
            # 获取第一条路线信息
            route = data['route']['paths'][0]
            
            # 提取基本信息
            distance = int(route.get('distance', 0))
            duration = int(route.get('duration', 0))
            traffic_lights = int(route.get('traffic_lights', 0))
            
            # 过路费信息
            tolls = int(route.get('tolls', 0))
            toll_distance = int(route.get('toll_distance', 0))
            
            # 路线策略描述
            strategy_map = {
                0: "速度优先",
                1: "费用优先", 
                2: "距离优先"
            }
            strategy_desc = strategy_map.get(settings.amap_strategy, "未知策略")
            
            # 步骤信息
            steps = route.get('steps', [])
            
            return RouteInfo(
                distance=distance,
                duration=duration,
                traffic_lights=traffic_lights,
                strategy=strategy_desc,
                tolls=tolls,
                toll_distance=toll_distance,
                steps=steps
            )
            
        except (KeyError, IndexError, ValueError) as e:
            logger.error("路线数据解析失败", error=str(e), raw_data=str(data)[:200])
            raise RouteCalculationError(f"路线数据格式错误: {str(e)}")
    
    async def get_traffic_condition(
        self,
        origin: str = None,
        destination: str = None
    ) -> TrafficCondition:
        """
        获取路况信息
        
        Args:
            origin: 出发地坐标
            destination: 目的地坐标
            
        Returns:
            TrafficCondition: 路况信息
        """
        origin = origin or settings.amap_origin
        destination = destination or settings.amap_destination
        
        logger.debug("获取路况信息", origin=origin, destination=destination)
        
        try:
            # 先获取路线信息
            route_info = await self.calculate_route(origin, destination)
            
            # 根据时长和距离计算平均速度
            if route_info.distance > 0 and route_info.duration > 0:
                # 速度 = 距离(km) / 时间(小时)
                speed_kmh = (route_info.distance / 1000) / (route_info.duration / 3600)
            else:
                speed_kmh = 0
            
            # 转换路况状态
            congestion_level = convert_speed_to_chinese(speed_kmh)
            
            return TrafficCondition(
                status="success",
                description=f"平均速度{speed_kmh:.1f}km/h",
                speed=speed_kmh,
                congestion_level=congestion_level
            )
            
        except Exception as e:
            logger.error("获取路况信息失败", error=str(e))
            return TrafficCondition(
                status="error",
                description="无法获取路况信息",
                speed=0,
                congestion_level="未知"
            )
    
    async def batch_calculate_routes(
        self,
        route_pairs: List[tuple]
    ) -> List[RouteInfo]:
        """
        批量计算多条路线
        
        Args:
            route_pairs: 路线对列表 [(origin, destination), ...]
            
        Returns:
            List[RouteInfo]: 路线信息列表
        """
        logger.info(f"开始批量计算{len(route_pairs)}条路线")
        
        tasks = [
            self.calculate_route(origin, dest) 
            for origin, dest in route_pairs
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果和异常
            route_infos = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"第{i+1}条路线计算失败", error=str(result))
                else:
                    route_infos.append(result)
            
            logger.info(f"批量路线计算完成，成功{len(route_infos)}条")
            return route_infos
            
        except Exception as e:
            logger.error("批量路线计算异常", error=str(e))
            raise RouteCalculationError(f"批量计算失败: {str(e)}")


# 便捷函数
async def get_route_info() -> RouteInfo:
    """获取当前配置的路线信息"""
    async with AMAPClient() as client:
        return await client.calculate_route()


async def get_traffic_status() -> TrafficCondition:
    """获取当前路况状态"""
    async with AMAPClient() as client:
        return await client.get_traffic_condition()