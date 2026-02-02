# -*- coding: utf-8 -*-
"""
简化版高德地图API调用
最简单的小白模式 - 只需要填写API Key就能使用
"""

import requests
import json
from datetime import datetime


def get_route_time(origin, destination, api_key):
    """
    获取路线时长（最简版本）
    
    参数:
        origin: 出发地坐标 "经度,纬度" 例如: "116.481485,39.990464"
        destination: 目的地坐标 "经度,纬度"
        api_key: 高德地图API Key
    
    返回:
        dict: 包含距离、时长等信息
    """
    
    # 高德地图驾车路线规划API
    url = "https://restapi.amap.com/v3/direction/driving"
    
    # 请求参数
    params = {
        'origin': origin,           # 出发地
        'destination': destination, # 目的地
        'key': api_key,            # API密钥
        'output': 'json',          # 返回格式
        'strategy': '0'            # 0-速度优先
    }
    
    try:
        # 发送请求
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析返回的JSON数据
        data = response.json()
        
        # 检查API调用是否成功
        if data.get('status') != '1':
            print(f"API调用失败: {data.get('info', '未知错误')}")
            return None
        
        # 提取路线信息
        route = data['route']
        paths = route['paths'][0]  # 取第一条路线
        
        # 获取距离和时长
        distance = int(paths['distance'])  # 米
        duration = int(paths['duration'])  # 秒
        
        # 转换为更友好的格式
        distance_km = round(distance / 1000, 1)  # 公里
        duration_min = round(duration / 60)      # 分钟
        
        result = {
            'distance_meter': distance,
            'distance_km': distance_km,
            'duration_second': duration,
            'duration_minute': duration_min,
            'success': True
        }
        
        print(f"路线查询成功!")
        print(f"距离: {distance_km} 公里")
        print(f"时长: {duration_min} 分钟")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except KeyError as e:
        print(f"数据解析错误: {e}")
        print("可能是API Key无效或者返回数据格式有变")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None


def format_travel_time(minutes):
    """
    格式化旅行时间显示
    """
    if minutes < 60:
        return f"{minutes}分钟"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours}小时"
        else:
            return f"{hours}小时{mins}分钟"


# 测试函数
def test_amap_api():
    """
    测试高德API功能
    """
    print("=== 高德地图路线查询测试 ===")
    
    # 这里需要替换为你的实际坐标和API Key
    test_origin = "116.481485,39.990464"      # 示例坐标
    test_destination = "116.481485,39.990464" # 示例坐标
    test_api_key = "your_api_key_here"        # 替换为你的API Key
    
    result = get_route_time(test_origin, test_destination, test_api_key)
    
    if result:
        print("\n测试结果:")
        print(f"距离: {result['distance_km']} 公里")
        print(f"时长: {format_travel_time(result['duration_minute'])}")
    else:
        print("测试失败，请检查API Key和网络连接")


if __name__ == "__main__":
    test_amap_api()