"""
集成测试
测试各个模块之间的协作
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.commute_service import CommuteService
from app.mcp.amap_client import AMAPClient, RouteInfo
from app.mcp.dingtalk_client import DingTalkClient, CommuteNotification
from app.workers.tasks import check_commute_and_notify, calculate_route, send_notification
from app.utils.exceptions import RouteCalculationError, MessageSendError


class TestIntegration:
    """集成测试类"""
    
    @pytest.fixture
    def mock_route_info(self):
        """模拟路线信息"""
        return RouteInfo(
            distance=15000,  # 15公里
            duration=1800,   # 30分钟
            traffic_lights=8,
            strategy="速度优先",
            tolls=0,
            toll_distance=0,
            steps=[]
        )
    
    @pytest.fixture
    def mock_notification_data(self):
        """模拟通知数据"""
        return {
            'departure_time': datetime.now(),
            'arrival_time': datetime.now(),
            'duration_minutes': 30,
            'distance_km': 15.0,
            'traffic_status': '畅通',
            'toll_fee': 0,
            'traffic_lights': 8
        }
    
    @pytest.mark.asyncio
    async def test_commute_service_full_flow(self, mock_route_info, mock_notification_data):
        """测试通勤服务完整流程"""
        service = CommuteService()
        
        # Mock AMAP客户端
        with patch.object(AMAPClient, '__aenter__', return_value=AsyncMock()) as mock_enter:
            mock_amap_client = AsyncMock()
            mock_amap_client.calculate_route.return_value = mock_route_info
            mock_amap_client.get_traffic_condition.return_value = Mock(
                status="success",
                description="平均速度45km/h",
                speed=45.0,
                congestion_level="畅通"
            )
            mock_enter.return_value = mock_amap_client
            
            # Mock钉钉客户端
            with patch.object(DingTalkClient, '__aenter__', return_value=AsyncMock()) as mock_ding_enter:
                mock_ding_client = AsyncMock()
                mock_ding_client.send_commute_notification.return_value = {
                    'errcode': 0,
                    'errmsg': 'ok',
                    'msgid': 'test_message_id'
                }
                mock_ding_client.health_check.return_value = True
                mock_ding_enter.return_value = mock_ding_client
                
                # 执行完整流程
                result = await service.check_and_notify_commute(send_notification=True)
                
                # 验证结果
                assert result['status'] == 'success'
                assert result['notification_sent'] is True
                assert 'route_info' in result
                assert 'traffic_info' in result
                assert result['message_id'] == 'test_message_id'
    
    @pytest.mark.asyncio
    async def test_commute_service_without_notification(self, mock_route_info):
        """测试不发送通知的通勤服务"""
        service = CommuteService()
        
        with patch.object(AMAPClient, '__aenter__', return_value=AsyncMock()) as mock_enter:
            mock_amap_client = AsyncMock()
            mock_amap_client.calculate_route.return_value = mock_route_info
            mock_amap_client.get_traffic_condition.return_value = Mock(
                status="success",
                description="测试路况",
                speed=40.0,
                congestion_level="缓行"
            )
            mock_enter.return_value = mock_amap_client
            
            # 不发送通知
            result = await service.check_and_notify_commute(send_notification=False)
            
            assert result['status'] == 'success'
            assert 'notification_sent' not in result
            assert 'route_info' in result
            assert 'traffic_info' in result
    
    @pytest.mark.asyncio
    async def test_commute_service_route_calculation_failure(self):
        """测试路线计算失败的情况"""
        service = CommuteService()
        
        with patch.object(AMAPClient, '__aenter__', return_value=AsyncMock()) as mock_enter:
            mock_amap_client = AsyncMock()
            mock_amap_client.calculate_route.side_effect = RouteCalculationError("API调用失败")
            mock_enter.return_value = mock_amap_client
            
            # Mock钉钉客户端用于发送错误通知
            with patch.object(DingTalkClient, '__aenter__', return_value=AsyncMock()) as mock_ding_enter:
                mock_ding_client = AsyncMock()
                mock_ding_client.send_error_notification.return_value = {
                    'errcode': 0,
                    'errmsg': 'ok'
                }
                mock_ding_enter.return_value = mock_ding_client
                
                # 应该抛出异常
                with pytest.raises(RouteCalculationError):
                    await service.check_and_notify_commute(send_notification=True)
    
    @pytest.mark.asyncio
    async def test_batch_route_checking(self):
        """测试批量路线检查"""
        service = CommuteService()
        
        # 模拟多个路线
        route_pairs = [
            ("116.481485,39.990464", "116.481485,39.990464"),
            ("116.481485,39.990464", "116.481485,39.990464")
        ]
        
        with patch.object(AMAPClient, '__aenter__', return_value=AsyncMock()) as mock_enter:
            mock_amap_client = AsyncMock()
            # 模拟两个成功的路线计算
            mock_route_info = Mock(
                distance=15000,
                duration=1800,
                traffic_lights=8,
                strategy="速度优先",
                tolls=0,
                toll_distance=0
            )
            mock_amap_client.calculate_route.return_value = mock_route_info
            mock_enter.return_value = mock_amap_client
            
            with patch.object(DingTalkClient, '__aenter__', return_value=AsyncMock()):
                results = await service.batch_check_routes(route_pairs, send_notifications=False)
                
                assert len(results) == 2
                assert all(result['status'] == 'success' for result in results)
                assert all('route_info' in result for result in results)
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        service = CommuteService()
        
        with patch.object(AMAPClient, '__aenter__', return_value=AsyncMock()) as mock_amap_enter:
            mock_amap_client = AsyncMock()
            mock_amap_client.calculate_route.return_value = Mock(distance=1000, duration=60)
            mock_amap_enter.return_value = mock_amap_client
            
            with patch.object(DingTalkClient, '__aenter__', return_value=AsyncMock()) as mock_ding_enter:
                mock_ding_client = AsyncMock()
                mock_ding_client.health_check.return_value = True
                mock_ding_enter.return_value = mock_ding_client
                
                result = await service.health_check()
                
                assert result['status'] == 'healthy'
                assert 'checks' in result
                assert result['checks']['amap_api']['status'] == 'healthy'
                assert result['checks']['dingtalk_api']['status'] == 'healthy'


class TestCeleryTasks:
    """Celery任务集成测试"""
    
    @pytest.mark.celery(task_always_eager=True)
    def test_calculate_route_task(self, mock_route_info):
        """测试路线计算任务"""
        with patch('app.workers.tasks.calculate_route.apply_async') as mock_apply:
            mock_apply.return_value.get.return_value = {
                'distance': 15000,
                'duration': 1800,
                'traffic_lights': 8,
                'strategy': '速度优先',
                'tolls': 0,
                'toll_distance': 0
            }
            
            # 直接调用任务函数进行测试
            with patch('app.mcp.amap_client.AMAPClient') as mock_client_class:
                mock_instance = AsyncMock()
                mock_instance.__aenter__.return_value = mock_instance
                mock_instance.calculate_route.return_value = mock_route_info
                mock_client_class.return_value = mock_instance
                
                # 注意：这里需要修改任务函数使其可测试
                # 在实际测试中可能需要重构任务函数
    
    @pytest.mark.celery(task_always_eager=True)
    def test_send_notification_task(self, mock_notification_data):
        """测试发送通知任务"""
        with patch('app.workers.tasks.send_notification.apply_async') as mock_apply:
            mock_apply.return_value.get.return_value = {
                'success': True,
                'message_id': 'test_id',
                'timestamp': datetime.now().isoformat()
            }
            
            # 测试数据验证
            notification = CommuteNotification(**mock_notification_data)
            assert notification.duration_minutes == 30
            assert notification.distance_km == 15.0
            assert notification.traffic_status == '畅通'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])