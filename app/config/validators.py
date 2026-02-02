"""
配置验证工具
提供配置项的有效性验证功能
"""

import re
from typing import Tuple, Dict, Any
from ..utils.exceptions import ConfigValidationError


def validate_coordinates(coordinate_str: str) -> Tuple[float, float]:
    """
    验证坐标格式 (经度,纬度)
    
    Args:
        coordinate_str: 坐标字符串，格式为 "经度,纬度"
        
    Returns:
        Tuple[float, float]: (经度, 纬度)
        
    Raises:
        ConfigValidationError: 当坐标格式不正确时
    """
    if not coordinate_str:
        raise ConfigValidationError("坐标不能为空")
    
    try:
        lon_lat = coordinate_str.split(',')
        if len(lon_lat) != 2:
            raise ConfigValidationError(f"坐标格式错误: {coordinate_str}，应为 '经度,纬度'")
        
        longitude = float(lon_lat[0].strip())
        latitude = float(lon_lat[1].strip())
        
        # 验证经纬度范围
        if not (-180 <= longitude <= 180):
            raise ConfigValidationError(f"经度超出范围[-180, 180]: {longitude}")
        if not (-90 <= latitude <= 90):
            raise ConfigValidationError(f"纬度超出范围[-90, 90]: {latitude}")
            
        return longitude, latitude
        
    except ValueError as e:
        raise ConfigValidationError(f"坐标值无效: {coordinate_str}")


def validate_amap_api_key(api_key: str) -> bool:
    """
    验证高德API Key格式
    
    Args:
        api_key: API Key字符串
        
    Returns:
        bool: 是否有效
    """
    if not api_key or len(api_key) < 10:
        return False
    # 简单的格式验证，实际应该根据高德API规则调整
    return bool(re.match(r'^[a-zA-Z0-9]+$', api_key))


def validate_dingtalk_webhook(url: str) -> bool:
    """
    验证钉钉Webhook URL格式
    
    Args:
        url: Webhook URL
        
    Returns:
        bool: 是否有效
    """
    if not url:
        return False
    
    import urllib.parse
    try:
        parsed = urllib.parse.urlparse(url)
        return all([parsed.scheme, parsed.netloc, 'dingtalk.com' in parsed.netloc])
    except Exception:
        return False


def validate_cron_expression(cron_expr: str) -> bool:
    """
    验证Cron表达式格式
    
    Args:
        cron_expr: Cron表达式
        
    Returns:
        bool: 是否有效
    """
    if not cron_expr:
        return False
    
    # 简单的格式验证 (秒 分 时 日 月 周)
    parts = cron_expr.strip().split()
    if len(parts) != 6:
        return False
    
    # 更严格的验证可以在这里添加
    return True


def validate_all_config(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证所有配置项
    
    Args:
        config_dict: 配置字典
        
    Returns:
        Dict[str, Any]: 验证后的配置
        
    Raises:
        ConfigValidationError: 当配置无效时
    """
    errors = []
    
    # 验证必需配置项
    required_fields = [
        'AMAP_API_KEY',
        'AMAP_ORIGIN', 
        'AMAP_DESTINATION',
        'DINGTALK_WEBHOOK_URL',
        'DINGTALK_SECRET'
    ]
    
    for field in required_fields:
        if not config_dict.get(field):
            errors.append(f"缺少必需配置项: {field}")
    
    # 验证坐标格式
    try:
        validate_coordinates(config_dict.get('AMAP_ORIGIN', ''))
    except ConfigValidationError as e:
        errors.append(f"出发地坐标错误: {str(e)}")
    
    try:
        validate_coordinates(config_dict.get('AMAP_DESTINATION', ''))
    except ConfigValidationError as e:
        errors.append(f"目的地坐标错误: {str(e)}")
    
    # 验证API Key
    if not validate_amap_api_key(config_dict.get('AMAP_API_KEY', '')):
        errors.append("高德API Key格式无效")
    
    # 验证钉钉配置
    if not validate_dingtalk_webhook(config_dict.get('DINGTALK_WEBHOOK_URL', '')):
        errors.append("钉钉Webhook URL格式无效")
    
    # 验证Cron表达式
    if not validate_cron_expression(config_dict.get('COMMUTE_CHECK_CRON', '')):
        errors.append("定时任务Cron表达式格式无效")
    
    if errors:
        raise ConfigValidationError("配置验证失败:\n" + "\n".join(errors))
    
    return config_dict