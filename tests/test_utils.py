"""
工具函数测试
"""

import pytest
from datetime import datetime, timedelta
from app.utils.helpers import (
    format_duration,
    calculate_eta,
    safe_json_parse,
    mask_sensitive_info,
    validate_chinese_mobile,
    get_current_timestamp,
    build_amap_request_params,
    convert_speed_to_chinese,
    calculate_statistics,
    is_weekday,
    next_weekday,
    truncate_string
)


class TestHelpers:
    """工具函数测试类"""
    
    def test_format_duration(self):
        """测试时长格式化"""
        # 分钟级别
        assert format_duration(30) == "30分钟"
        assert format_duration(59) == "59分钟"
        
        # 小时级别
        assert format_duration(60) == "1小时"
        assert format_duration(90) == "1小时30分钟"
        assert format_duration(120) == "2小时"
        
        # 天级别
        assert format_duration(1440) == "1天"  # 24小时
        assert format_duration(1500) == "1天1小时"  # 25小时
        assert format_duration(2880) == "2天"  # 48小时
    
    def test_calculate_eta(self):
        """测试预计到达时间计算"""
        departure = datetime(2024, 1, 1, 8, 0, 0)
        
        # 30分钟行程
        eta = calculate_eta(departure, 30)
        expected = datetime(2024, 1, 1, 8, 30, 0)
        assert eta == expected
        
        # 90分钟行程
        eta = calculate_eta(departure, 90)
        expected = datetime(2024, 1, 1, 9, 30, 0)
        assert eta == expected
    
    def test_safe_json_parse(self):
        """测试安全JSON解析"""
        # 有效JSON
        result = safe_json_parse('{"key": "value"}')
        assert result == {"key": "value"}
        
        # 无效JSON
        result = safe_json_parse('invalid json', default={"default": "value"})
        assert result == {"default": "value"}
        
        # None输入
        result = safe_json_parse(None, default="default")
        assert result == "default"
    
    def test_mask_sensitive_info(self):
        """测试敏感信息遮蔽"""
        # 正常长度
        assert mask_sensitive_info("12345678901") == "12*******01"
        assert mask_sensitive_info("abcdefghijklmnop") == "ab************op"
        
        # 短字符串
        assert mask_sensitive_info("123") == "123"
        assert mask_sensitive_info("ab") == "ab"
        
        # 空字符串
        assert mask_sensitive_info("") == ""
        assert mask_sensitive_info(None) == None
    
    def test_validate_chinese_mobile(self):
        """测试中国手机号验证"""
        # 有效手机号
        assert validate_chinese_mobile("13812345678") is True
        assert validate_chinese_mobile("15912345678") is True
        assert validate_chinese_mobile("18812345678") is True
        
        # 无效手机号
        assert validate_chinese_mobile("12812345678") is False  # 不是1开头
        assert validate_chinese_mobile("1381234567") is False   # 长度不够
        assert validate_chinese_mobile("138123456789") is False  # 长度太长
        assert validate_chinese_mobile("") is False
        assert validate_chinese_mobile(None) is False
    
    def test_get_current_timestamp(self):
        """测试时间戳获取"""
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0
        # 验证是毫秒级时间戳
        assert len(str(timestamp)) >= 13
    
    def test_build_amap_request_params(self):
        """测试高德地图请求参数构建"""
        params = build_amap_request_params(
            origin="116.481485,39.990464",
            destination="116.481485,39.990464",
            key="test_key",
            strategy=0
        )
        
        expected = {
            'origin': '116.481485,39.990464',
            'destination': '116.481485,39.990464',
            'key': 'test_key',
            'strategy': '0',
            'output': 'json',
            'extensions': 'base'
        }
        
        assert params == expected
    
    def test_convert_speed_to_chinese(self):
        """测试速度转换为中文描述"""
        # 畅通
        assert convert_speed_to_chinese(85) == "畅通"
        assert convert_speed_to_chinese(80) == "畅通"
        
        # 缓行
        assert convert_speed_to_chinese(79) == "缓行"
        assert convert_speed_to_chinese(60) == "缓行"
        
        # 拥堵
        assert convert_speed_to_chinese(59) == "拥堵"
        assert convert_speed_to_chinese(30) == "拥堵"
        
        # 严重拥堵
        assert convert_speed_to_chinese(29) == "严重拥堵"
        assert convert_speed_to_chinese(0) == "严重拥堵"
    
    def test_calculate_statistics(self):
        """测试统计数据计算"""
        # 正常数据
        data = [10, 20, 30, 40, 50]
        stats = calculate_statistics(data)
        
        assert stats['count'] == 5
        assert stats['average'] == 30
        assert stats['max'] == 50
        assert stats['min'] == 10
        assert stats['total'] == 150
        
        # 空数据
        stats = calculate_statistics([])
        assert stats['count'] == 0
        assert stats['average'] == 0
        assert stats['max'] == 0
        assert stats['min'] == 0
        assert stats['total'] == 0
        
        # 单个数据
        stats = calculate_statistics([42])
        assert stats['count'] == 1
        assert stats['average'] == 42
        assert stats['max'] == 42
        assert stats['min'] == 42
        assert stats['total'] == 42
    
    def test_is_weekday(self):
        """测试工作日判断"""
        # 周一到周五是工作日
        monday = datetime(2024, 1, 1)  # 周一
        assert is_weekday(monday) is True
        
        friday = datetime(2024, 1, 5)  # 周五
        assert is_weekday(friday) is True
        
        # 周六周日不是工作日
        saturday = datetime(2024, 1, 6)  # 周六
        assert is_weekday(saturday) is False
        
        sunday = datetime(2024, 1, 7)  # 周日
        assert is_weekday(sunday) is False
    
    def test_next_weekday(self):
        """测试获取下一个工作日"""
        # 周五的下一个工作日是下周一
        friday = datetime(2024, 1, 5)
        next_workday = next_weekday(friday)
        assert next_workday.weekday() == 0  # 周一
        assert (next_workday - friday).days == 3
        
        # 周一的下一个工作日是周二
        monday = datetime(2024, 1, 1)
        next_workday = next_weekday(monday)
        assert next_workday.weekday() == 1  # 周二
        assert (next_workday - monday).days == 1
    
    def test_truncate_string(self):
        """测试字符串截断"""
        # 短字符串不需要截断
        assert truncate_string("hello", 10) == "hello"
        
        # 长字符串需要截断
        result = truncate_string("this is a very long string", 15)
        assert len(result) == 15
        assert result.endswith("...")
        
        # 自定义后缀
        result = truncate_string("hello world", 8, "~~~")
        assert result == "hello~~~"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])