"""
通用工具函数
提供各种辅助功能函数
"""

import hashlib
import hmac
import base64
import time
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote_plus


def generate_dingtalk_signature(secret: str, timestamp: int) -> str:
    """
    生成钉钉签名
    
    Args:
        secret: 钉钉机器人密钥
        timestamp: 时间戳
        
    Returns:
        str: 签名字符串
    """
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return quote_plus(base64.b64encode(hmac_code))


def format_duration(minutes: int) -> str:
    """
    格式化时长显示
    
    Args:
        minutes: 分钟数
        
    Returns:
        str: 格式化的时长字符串
    """
    if minutes < 60:
        return f"{minutes}分钟"
    elif minutes < 1440:  # 24小时
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours}小时"
        else:
            return f"{hours}小时{remaining_minutes}分钟"
    else:
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days}天"
        else:
            return f"{days}天{remaining_hours}小时"


def calculate_eta(departure_time: datetime, duration_minutes: int) -> datetime:
    """
    计算预计到达时间
    
    Args:
        departure_time: 出发时间
        duration_minutes: 行程时长（分钟）
        
    Returns:
        datetime: 预计到达时间
    """
    return departure_time + timedelta(minutes=duration_minutes)


def safe_json_parse(json_string: str, default: Any = None) -> Any:
    """
    安全的JSON解析
    
    Args:
        json_string: JSON字符串
        default: 解析失败时的默认值
        
    Returns:
        解析结果或默认值
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def mask_sensitive_info(text: str, mask_char: str = "*") -> str:
    """
    遮蔽敏感信息
    
    Args:
        text: 原始文本
        mask_char: 遮蔽字符
        
    Returns:
        str: 遮蔽后的文本
    """
    if not text or len(text) <= 4:
        return text
    
    # 保留前2位和后2位，中间用遮蔽字符替换
    return text[:2] + mask_char * (len(text) - 4) + text[-2:]


def validate_chinese_mobile(phone: str) -> bool:
    """
    验证中国手机号码格式
    
    Args:
        phone: 手机号码字符串
        
    Returns:
        bool: 是否为有效的中国手机号码
    """
    import re
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def get_current_timestamp() -> int:
    """
    获取当前时间戳（毫秒）
    
    Returns:
        int: 当前时间戳
    """
    return int(time.time() * 1000)


def build_amap_request_params(origin: str, destination: str, key: str, strategy: int = 0) -> Dict[str, str]:
    """
    构建高德地图API请求参数
    
    Args:
        origin: 出发地坐标 "经度,纬度"
        destination: 目的地坐标 "经度,纬度"  
        key: API Key
        strategy: 路线策略
        
    Returns:
        Dict[str, str]: 请求参数字典
    """
    return {
        'origin': origin,
        'destination': destination,
        'key': key,
        'strategy': str(strategy),
        'output': 'json',
        'extensions': 'base'
    }


def convert_speed_to_chinese(speed: float) -> str:
    """
    将速度转换为中文描述
    
    Args:
        speed: 速度（km/h）
        
    Returns:
        str: 中文速度描述
    """
    if speed >= 80:
        return "畅通"
    elif speed >= 60:
        return "缓行"
    elif speed >= 30:
        return "拥堵"
    else:
        return "严重拥堵"


def calculate_statistics(data_list: list) -> Dict[str, Union[int, float]]:
    """
    计算数据统计信息
    
    Args:
        data_list: 数值列表
        
    Returns:
        Dict: 包含平均值、最大值、最小值等统计信息
    """
    if not data_list:
        return {
            'count': 0,
            'average': 0,
            'max': 0,
            'min': 0,
            'total': 0
        }
    
    return {
        'count': len(data_list),
        'average': sum(data_list) / len(data_list),
        'max': max(data_list),
        'min': min(data_list),
        'total': sum(data_list)
    }


def is_weekday(date: datetime = None) -> bool:
    """
    判断是否为工作日
    
    Args:
        date: 日期，默认为今天
        
    Returns:
        bool: 是否为工作日（周一到周五）
    """
    if date is None:
        date = datetime.now()
    return date.weekday() < 5  # 0-4 是周一到周五


def next_weekday(current_date: datetime = None) -> datetime:
    """
    获取下一个工作日
    
    Args:
        current_date: 当前日期
        
    Returns:
        datetime: 下一个工作日
    """
    if current_date is None:
        current_date = datetime.now()
    
    next_day = current_date + timedelta(days=1)
    while not is_weekday(next_day):
        next_day += timedelta(days=1)
    
    return next_day


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix