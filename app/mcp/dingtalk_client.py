"""
钉钉MCP客户端
实现消息推送功能
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel

from ..config.settings import settings
from ..utils.logger import get_logger
from ..utils.exceptions import DingTalkAPIError, MessageSendError
from ..utils.error_handler import retry, NETWORK_RETRY_CONFIG
from ..utils.helpers import generate_dingtalk_signature, get_current_timestamp, format_duration

logger = get_logger(__name__)


class MessageTemplate(BaseModel):
    """消息模板基类"""
    msgtype: str
    content: Dict[str, Any]


class TextMessage(MessageTemplate):
    """文本消息"""
    msgtype: str = "text"
    
    def __init__(self, content: str, at_mobiles: List[str] = None, is_at_all: bool = False):
        super().__init__(
            msgtype="text",
            content={
                "content": content,
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": is_at_all
                }
            }
        )


class MarkdownMessage(MessageTemplate):
    """Markdown消息"""
    msgtype: str = "markdown"
    
    def __init__(self, title: str, text: str, at_mobiles: List[str] = None, is_at_all: bool = False):
        super().__init__(
            msgtype="markdown",
            content={
                "title": title,
                "text": text,
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": is_at_all
                }
            }
        )


class CommuteNotification(BaseModel):
    """通勤通知数据模型"""
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    distance_km: float
    traffic_status: str
    toll_fee: int
    traffic_lights: int
    weather_info: Optional[str] = None


class DingTalkClient:
    """钉钉机器人客户端"""
    
    def __init__(self):
        self.webhook_url = settings.dingtalk_webhook_url
        self.secret = settings.dingtalk_secret
        self.keyword = settings.dingtalk_keyword
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
    
    def _generate_signed_url(self) -> str:
        """
        生成带签名的Webhook URL
        
        Returns:
            str: 带签名的完整URL
        """
        timestamp = get_current_timestamp()
        signature = generate_dingtalk_signature(self.secret, timestamp)
        
        # 在URL中添加时间戳和签名参数
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed_url = urlparse(self.webhook_url)
        query_params = parse_qs(parsed_url.query)
        query_params.update({
            'timestamp': str(timestamp),
            'sign': signature
        })
        
        # 重新构建URL
        new_query = urlencode(query_params, doseq=True)
        signed_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return signed_url
    
    @retry(config=NETWORK_RETRY_CONFIG)
    async def _send_message(self, message: MessageTemplate) -> Dict[str, Any]:
        """
        发送消息到钉钉
        
        Args:
            message: 消息对象
            
        Returns:
            Dict: API响应
            
        Raises:
            DingTalkAPIError: 消息发送失败
        """
        if not self.client:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        
        # 生成签名URL
        signed_url = self._generate_signed_url()
        
        try:
            # 发送POST请求
            response = await self.client.post(
                signed_url,
                json=message.dict(),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 检查响应状态
            if data.get('errcode') != 0:
                error_msg = data.get('errmsg', '未知错误')
                raise DingTalkAPIError(f"钉钉消息发送失败: {error_msg}")
            
            logger.info("钉钉消息发送成功", message_type=message.msgtype)
            return data
            
        except httpx.RequestError as e:
            logger.error(f"钉钉消息网络请求失败: {str(e)}")
            raise DingTalkAPIError(f"网络请求失败: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"钉钉消息HTTP错误: {e.response.status_code}")
            raise DingTalkAPIError(
                f"HTTP错误: {e.response.status_code}",
                status_code=e.response.status_code
            )
    
    async def send_text_message(
        self, 
        content: str, 
        at_mobiles: List[str] = None, 
        is_at_all: bool = False
    ) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            at_mobiles: 需要@的手机号列表
            is_at_all: 是否@所有人
            
        Returns:
            Dict: API响应
        """
        # 添加关键词确保消息能发送成功
        if self.keyword and self.keyword not in content:
            content = f"[{self.keyword}] {content}"
        
        message = TextMessage(content, at_mobiles, is_at_all)
        return await self._send_message(message)
    
    async def send_markdown_message(
        self,
        title: str,
        text: str,
        at_mobiles: List[str] = None,
        is_at_all: bool = False
    ) -> Dict[str, Any]:
        """
        发送Markdown消息
        
        Args:
            title: 消息标题
            text: Markdown内容
            at_mobiles: 需要@的手机号列表
            is_at_all: 是否@所有人
            
        Returns:
            Dict: API响应
        """
        # 添加关键词确保消息能发送成功
        if self.keyword and self.keyword not in title:
            title = f"[{self.keyword}] {title}"
        
        message = MarkdownMessage(title, text, at_mobiles, is_at_all)
        return await self._send_message(message)
    
    async def send_commute_notification(
        self,
        notification: CommuteNotification
    ) -> Dict[str, Any]:
        """
        发送通勤通知
        
        Args:
            notification: 通勤通知数据
            
        Returns:
            Dict: API响应
        """
        # 格式化时间
        departure_str = notification.departure_time.strftime("%H:%M")
        arrival_str = notification.arrival_time.strftime("%H:%M")
        
        # 构建Markdown消息
        title = f"🚗 今日通勤提醒 - {departure_str}出发"
        
        content_lines = [
            f"## 🚗 通勤路线信息",
            f"",
            f"**出发时间**: {departure_str}",
            f"**预计到达**: {arrival_str}",
            f"**行程时长**: {format_duration(notification.duration_minutes)}",
            f"**行驶距离**: {notification.distance_km:.1f}公里",
            f"**路况状态**: {notification.traffic_status}",
            f"",
            f"📊 **详细信息**:",
            f"- 红绿灯数量: {notification.traffic_lights}个",
            f"- 过路费用: {notification.toll_fee}元"
        ]
        
        if notification.weather_info:
            content_lines.extend([
                f"- 天气状况: {notification.weather_info}"
            ])
        
        content_lines.extend([
            f"",
            f"⏰ 温馨提示：建议提前规划出行时间",
            f"",
            f"> 本消息由智能通勤助手自动发送"
        ])
        
        content = "\n".join(content_lines)
        
        logger.info(
            "发送通勤通知",
            departure=departure_str,
            duration=notification.duration_minutes,
            distance=notification.distance_km
        )
        
        return await self.send_markdown_message(title, content)
    
    async def send_error_notification(
        self,
        error_title: str,
        error_message: str,
        error_time: datetime = None
    ) -> Dict[str, Any]:
        """
        发送错误通知
        
        Args:
            error_title: 错误标题
            error_message: 错误详情
            error_time: 错误发生时间
            
        Returns:
            Dict: API响应
        """
        if error_time is None:
            error_time = datetime.now()
        
        title = f"⚠️ 系统异常通知 - {error_time.strftime('%H:%M')}"
        
        content = f"""## ⚠️ 系统异常

**异常时间**: {error_time.strftime('%Y-%m-%d %H:%M:%S')}
**异常类型**: {error_title}

**详细信息**:
```
{error_message}
```

请及时检查系统运行状态。
"""
        
        logger.error("发送错误通知", error_type=error_title)
        return await self.send_markdown_message(title, content)
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 是否健康
        """
        try:
            # 发送简单的测试消息
            test_message = "🔧 系统健康检查 - 服务正常运行"
            await self.send_text_message(test_message)
            return True
        except Exception as e:
            logger.error("健康检查失败", error=str(e))
            return False


# 便捷函数
async def send_commute_alert(notification: CommuteNotification) -> Dict[str, Any]:
    """发送通勤提醒"""
    async with DingTalkClient() as client:
        return await client.send_commute_notification(notification)


async def send_system_error(error_title: str, error_message: str) -> Dict[str, Any]:
    """发送系统错误通知"""
    async with DingTalkClient() as client:
        return await client.send_error_notification(error_title, error_message)


async def send_simple_message(content: str) -> Dict[str, Any]:
    """发送简单文本消息"""
    async with DingTalkClient() as client:
        return await client.send_text_message(content)