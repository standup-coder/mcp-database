"""
Celery任务定义
实现具体的业务逻辑任务
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .celery_app import celery_app
from ..utils.logger import get_logger
from ..utils.logging_context import commute_check_context, route_calculation_context, message_send_context
from ..utils.error_handler import handle_exceptions
from ..mcp.amap_client import AMAPClient, RouteInfo
from ..mcp.dingtalk_client import DingTalkClient, CommuteNotification
from ..utils.exceptions import TaskExecutionError

logger = get_logger(__name__)


@celery_app.task(bind=True, name='app.workers.tasks.check_commute_and_notify')
@commute_check_context()
@handle_exceptions(reraise=True)
def check_commute_and_notify(self) -> Dict[str, Any]:
    """
    检查通勤路线并发送通知的主要任务
    
    Returns:
        Dict: 任务执行结果
    """
    logger.info("开始执行每日通勤检查任务")
    
    try:
        # 1. 计算路线信息
        route_info = calculate_route.delay().get()
        
        if not route_info:
            raise TaskExecutionError("路线计算失败，无法获取路线信息")
        
        # 2. 构造通知数据
        notification_data = construct_notification_data(route_info)
        
        # 3. 发送钉钉通知
        result = send_notification.delay(notification_data).get()
        
        logger.info("通勤检查任务执行完成", result=result)
        
        return {
            'status': 'success',
            'task_id': self.request.id,
            'execution_time': datetime.now().isoformat(),
            'route_info': route_info,
            'notification_sent': result.get('success', False) if result else False
        }
        
    except Exception as e:
        logger.error("通勤检查任务执行失败", error=str(e))
        
        # 发送错误通知
        try:
            error_result = send_system_error.delay(
                "通勤检查任务失败",
                str(e)
            ).get()
            logger.info("错误通知已发送", result=error_result)
        except Exception as notify_error:
            logger.error("发送错误通知也失败了", error=str(notify_error))
        
        raise TaskExecutionError(f"通勤检查任务失败: {str(e)}")


@celery_app.task(bind=True, name='app.workers.tasks.calculate_route')
@route_calculation_context()
@handle_exceptions(default_return=None)
def calculate_route(self) -> Optional[Dict[str, Any]]:
    """
    计算路线信息的任务
    
    Returns:
        Dict: 路线信息字典
    """
    logger.info("开始计算通勤路线")
    
    try:
        import asyncio
        
        async def _calculate():
            async with AMAPClient() as client:
                route_info = await client.calculate_route()
                return {
                    'distance': route_info.distance,
                    'duration': route_info.duration,
                    'traffic_lights': route_info.traffic_lights,
                    'strategy': route_info.strategy,
                    'tolls': route_info.tolls,
                    'toll_distance': route_info.toll_distance
                }
        
        # 在事件循环中运行异步代码
        route_data = asyncio.run(_calculate())
        
        logger.info(
            "路线计算完成",
            distance=f"{route_data['distance']}米",
            duration=f"{route_data['duration']}秒"
        )
        
        return route_data
        
    except Exception as e:
        logger.error("路线计算任务失败", error=str(e))
        raise TaskExecutionError(f"路线计算失败: {str(e)}")


@celery_app.task(bind=True, name='app.workers.tasks.send_notification')
@message_send_context()
@handle_exceptions(default_return={'success': False})
def send_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    发送通知的任务
    
    Args:
        notification_data: 通知数据
        
    Returns:
        Dict: 发送结果
    """
    logger.info("开始发送通勤通知")
    
    try:
        import asyncio
        
        # 构造通知对象
        notification = CommuteNotification(**notification_data)
        
        async def _send():
            async with DingTalkClient() as client:
                return await client.send_commute_notification(notification)
        
        # 发送通知
        result = asyncio.run(_send())
        
        logger.info("通勤通知发送完成", result=result)
        
        return {
            'success': True,
            'message_id': result.get('msgid', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("通知发送任务失败", error=str(e))
        raise TaskExecutionError(f"通知发送失败: {str(e)}")


@celery_app.task(bind=True, name='app.workers.tasks.health_check')
@handle_exceptions(default_return={'status': 'failed'})
def health_check(self) -> Dict[str, Any]:
    """
    系统健康检查任务
    
    Returns:
        Dict: 健康检查结果
    """
    logger.info("开始执行系统健康检查")
    
    try:
        import asyncio
        
        async def _check_health():
            async with DingTalkClient() as client:
                return await client.health_check()
        
        # 执行健康检查
        is_healthy = asyncio.run(_check_health())
        
        result = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
        
        logger.info("健康检查完成", result=result)
        return result
        
    except Exception as e:
        logger.error("健康检查任务失败", error=str(e))
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='app.workers.tasks.cleanup_expired_results')
@handle_exceptions(default_return={'status': 'failed'})
def cleanup_expired_results(self) -> Dict[str, Any]:
    """
    清理过期任务结果
    
    Returns:
        Dict: 清理结果
    """
    logger.info("开始清理过期任务结果")
    
    try:
        from celery.result import AsyncResult
        
        # 这里可以添加具体的清理逻辑
        # 例如清理数据库中的过期记录等
        
        result = {
            'status': 'completed',
            'cleaned_count': 0,  # 实际实现时需要统计清理的数量
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("过期结果清理完成", result=result)
        return result
        
    except Exception as e:
        logger.error("清理任务失败", error=str(e))
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='app.workers.tasks.send_system_error')
@handle_exceptions(default_return={'success': False})
def send_system_error(self, error_title: str, error_message: str) -> Dict[str, Any]:
    """
    发送系统错误通知
    
    Args:
        error_title: 错误标题
        error_message: 错误消息
        
    Returns:
        Dict: 发送结果
    """
    logger.info("发送系统错误通知", error_title=error_title)
    
    try:
        import asyncio
        
        async def _send_error():
            async with DingTalkClient() as client:
                return await client.send_error_notification(error_title, error_message)
        
        result = asyncio.run(_send_error())
        
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


def construct_notification_data(route_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    构造通知数据
    
    Args:
        route_info: 路线信息
        
    Returns:
        Dict: 通知数据
    """
    now = datetime.now()
    
    # 计算相关信息
    duration_minutes = route_info['duration'] // 60
    distance_km = route_info['distance'] / 1000
    arrival_time = datetime.now().replace(
        hour=(now.hour + duration_minutes // 60) % 24,
        minute=(now.minute + duration_minutes % 60) % 60
    )
    
    # 简单的路况判断（可以根据实际需求优化）
    avg_speed = distance_km / (duration_minutes / 60) if duration_minutes > 0 else 0
    if avg_speed > 40:
        traffic_status = "🟢 畅通"
    elif avg_speed > 20:
        traffic_status = "🟡 缓行"
    else:
        traffic_status = "🔴 拥堵"
    
    return {
        'departure_time': now,
        'arrival_time': arrival_time,
        'duration_minutes': duration_minutes,
        'distance_km': round(distance_km, 1),
        'traffic_status': traffic_status,
        'toll_fee': route_info['tolls'],
        'traffic_lights': route_info['traffic_lights']
    }