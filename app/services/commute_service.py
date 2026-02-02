"""
通勤服务层
整合路线查询和消息推送的核心业务逻辑
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import asyncio

from ..utils.logger import get_logger
from ..utils.logging_context import commute_check_context
from ..utils.error_handler import handle_exceptions
from ..mcp.amap_client import AMAPClient, RouteInfo, TrafficCondition
from ..mcp.dingtalk_client import DingTalkClient, CommuteNotification
from ..utils.exceptions import RouteCalculationError, MessageSendError
from ..config.settings import settings

logger = get_logger(__name__)


class CommuteService:
    """通勤服务类"""
    
    def __init__(self):
        self.amap_client = AMAPClient()
        self.dingtalk_client = DingTalkClient()
    
    @commute_check_context()
    @handle_exceptions(reraise=True)
    async def check_and_notify_commute(
        self,
        origin: str = None,
        destination: str = None,
        send_notification: bool = True
    ) -> Dict[str, Any]:
        """
        检查通勤路线并发送通知
        
        Args:
            origin: 出发地坐标
            destination: 目的地坐标
            send_notification: 是否发送通知
            
        Returns:
            Dict: 执行结果
        """
        logger.info("开始通勤检查流程")
        
        try:
            # 1. 计算路线信息
            route_info = await self._calculate_route(origin, destination)
            
            # 2. 获取路况信息
            traffic_info = await self._get_traffic_info(origin, destination)
            
            # 3. 构造通知数据
            notification_data = self._build_notification_data(route_info, traffic_info)
            
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'route_info': route_info.dict() if hasattr(route_info, 'dict') else route_info,
                'traffic_info': traffic_info.dict() if hasattr(traffic_info, 'dict') else traffic_info
            }
            
            # 4. 发送通知（如果需要）
            if send_notification:
                notification_result = await self._send_commute_notification(notification_data)
                result['notification_sent'] = notification_result.get('success', False)
                result['message_id'] = notification_result.get('message_id')
            
            logger.info("通勤检查流程完成", result=result)
            return result
            
        except Exception as e:
            logger.error("通勤检查流程失败", error=str(e))
            
            # 发送错误通知
            if send_notification:
                await self._send_error_notification("通勤检查失败", str(e))
            
            raise
    
    async def _calculate_route(
        self,
        origin: str = None,
        destination: str = None
    ) -> RouteInfo:
        """计算路线"""
        logger.debug("计算通勤路线")
        
        try:
            async with self.amap_client as client:
                route_info = await client.calculate_route(origin, destination)
                logger.info(
                    "路线计算完成",
                    distance=f"{route_info.distance}米",
                    duration=f"{route_info.duration}秒"
                )
                return route_info
                
        except Exception as e:
            logger.error("路线计算失败", error=str(e))
            raise RouteCalculationError(f"路线计算失败: {str(e)}")
    
    async def _get_traffic_info(
        self,
        origin: str = None,
        destination: str = None
    ) -> TrafficCondition:
        """获取路况信息"""
        logger.debug("获取路况信息")
        
        try:
            async with self.amap_client as client:
                traffic_info = await client.get_traffic_condition(origin, destination)
                logger.debug("路况信息获取完成", status=traffic_info.status)
                return traffic_info
                
        except Exception as e:
            logger.warning("路况信息获取失败", error=str(e))
            # 返回默认路况信息
            return TrafficCondition(
                status="unknown",
                description="无法获取实时路况",
                speed=0,
                congestion_level="未知"
            )
    
    def _build_notification_data(
        self,
        route_info: RouteInfo,
        traffic_info: TrafficCondition
    ) -> Dict[str, Any]:
        """构造通知数据"""
        now = datetime.now()
        
        # 计算相关信息
        duration_minutes = route_info.duration // 60
        distance_km = route_info.distance / 1000
        
        # 计算预计到达时间
        arrival_time = now + timedelta(minutes=duration_minutes)
        
        # 整合路况信息
        traffic_status = traffic_info.congestion_level
        if traffic_info.description and traffic_info.description != "无法获取实时路况":
            traffic_status = f"{traffic_status} ({traffic_info.description})"
        
        return {
            'departure_time': now,
            'arrival_time': arrival_time,
            'duration_minutes': duration_minutes,
            'distance_km': round(distance_km, 1),
            'traffic_status': traffic_status,
            'toll_fee': route_info.tolls,
            'traffic_lights': route_info.traffic_lights,
            'strategy': route_info.strategy
        }
    
    async def _send_commute_notification(
        self,
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """发送通勤通知"""
        logger.info("发送通勤通知")
        
        try:
            notification = CommuteNotification(**notification_data)
            
            async with self.dingtalk_client as client:
                result = await client.send_commute_notification(notification)
                
                return {
                    'success': True,
                    'message_id': result.get('msgid', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error("通勤通知发送失败", error=str(e))
            raise MessageSendError(f"通知发送失败: {str(e)}")
    
    async def _send_error_notification(
        self,
        error_title: str,
        error_message: str
    ) -> Dict[str, Any]:
        """发送错误通知"""
        logger.info("发送错误通知", error_type=error_title)
        
        try:
            async with self.dingtalk_client as client:
                result = await client.send_error_notification(error_title, error_message)
                
                return {
                    'success': True,
                    'message_id': result.get('msgid', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error("错误通知发送失败", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def batch_check_routes(
        self,
        route_pairs: List[tuple],
        send_notifications: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量检查多条路线
        
        Args:
            route_pairs: 路线对列表 [(origin, destination), ...]
            send_notifications: 是否发送通知
            
        Returns:
            List[Dict]: 检查结果列表
        """
        logger.info(f"开始批量检查{len(route_pairs)}条路线")
        
        results = []
        
        for i, (origin, destination) in enumerate(route_pairs):
            try:
                result = await self.check_and_notify_commute(
                    origin=origin,
                    destination=destination,
                    send_notification=send_notifications
                )
                result['route_index'] = i
                results.append(result)
                
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'route_index': i,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results.append(error_result)
                logger.error(f"第{i+1}条路线检查失败", error=str(e))
        
        logger.info(f"批量路线检查完成，共处理{len(results)}条路线")
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """
        服务健康检查
        
        Returns:
            Dict: 健康检查结果
        """
        logger.info("执行服务健康检查")
        
        checks = {}
        
        # 检查高德地图API
        try:
            async with self.amap_client as client:
                route_info = await client.calculate_route()
                checks['amap_api'] = {
                    'status': 'healthy',
                    'response_time': 'normal'
                }
        except Exception as e:
            checks['amap_api'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # 检查钉钉API
        try:
            async with self.dingtalk_client as client:
                is_healthy = await client.health_check()
                checks['dingtalk_api'] = {
                    'status': 'healthy' if is_healthy else 'unhealthy'
                }
        except Exception as e:
            checks['dingtalk_api'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # 总体健康状态
        overall_status = 'healthy' if all(
            check.get('status') == 'healthy' 
            for check in checks.values()
        ) else 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': checks
        }


# 便捷函数
async def check_daily_commute() -> Dict[str, Any]:
    """每日通勤检查"""
    service = CommuteService()
    return await service.check_and_notify_commute()


async def check_multiple_routes(route_pairs: List[tuple]) -> List[Dict[str, Any]]:
    """检查多条路线"""
    service = CommuteService()
    return await service.batch_check_routes(route_pairs)