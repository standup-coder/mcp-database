# -*- coding: utf-8 -*-
"""
一体化通勤助手 - dumb模式
最简单的小白版本，一个文件搞定所有功能
只需要填写你的配置信息就能运行
"""

import time
import json
from datetime import datetime

# 导入我们写的模块
from simple_amap import get_route_time, format_travel_time
from simple_dingtalk import send_commute_notification

# ==================== 配置区域（请在这里填写你的信息）====================

# 高德地图配置
AMAP_API_KEY = "在这里填写你的高德API Key"  # 从高德开放平台获取
HOME_LOCATION = "116.481485,39.990464"      # 家的坐标（经度,纬度）
WORK_LOCATION = "116.481485,39.990464"     # 公司的坐标（经度,纬度）

# 钉钉配置
DINGTALK_WEBHOOK = "在这里填写你的钉钉Webhook URL"  # 从钉钉群机器人获取
DINGTALK_SECRET = "在这里填写钉钉加签密钥（如果没有可以留空）"  # 可选

# ======================================================================


def check_commute_and_notify():
    """
    检查通勤路线并发送通知 - 一体化函数
    """
    print("=" * 50)
    print("🚀 开始执行通勤检查...")
    print("=" * 50)
    
    # 1. 获取当前时间
    current_time = datetime.now()
    print(f"⏰ 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. 查询路线信息
    print(f"\n📍 查询路线: {HOME_LOCATION} → {WORK_LOCATION}")
    print("📡 正在调用高德地图API...")
    
    route_info = get_route_time(HOME_LOCATION, WORK_LOCATION, AMAP_API_KEY)
    
    if not route_info:
        print("❌ 路线查询失败!")
        return False
    
    # 3. 显示路线详情
    print(f"\n📊 路线详情:")
    print(f"   距离: {route_info['distance_km']} 公里")
    print(f"   时长: {format_travel_time(route_info['duration_minute'])}")
    print(f"   平均速度: {round(route_info['distance_km'] / (route_info['duration_minute'] / 60), 1)} km/h")
    
    # 4. 发送钉钉通知
    print(f"\n📤 准备发送钉钉通知...")
    success = send_commute_notification(DINGTALK_WEBHOOK, route_info, DINGTALK_SECRET)
    
    if success:
        print("✅ 通勤检查完成!")
        return True
    else:
        print("❌ 通知发送失败!")
        return False


def run_manual_check():
    """
    手动执行一次通勤检查
    """
    print("🎯 手动通勤检查模式")
    return check_commute_and_notify()


def run_scheduled_check(hour=8, minute=30):
    """
    定时执行通勤检查
    
    参数:
        hour: 小时 (0-23)
        minute: 分钟 (0-59)
    """
    print(f"⏰ 定时模式: 每天 {hour:02d}:{minute:02d} 执行")
    
    while True:
        now = datetime.now()
        
        # 检查是否到了执行时间
        if now.hour == hour and now.minute == minute:
            print(f"\n🔔 到达预定时间 {hour:02d}:{minute:02d}")
            check_commute_and_notify()
            
            # 等待一分钟避免重复执行
            time.sleep(60)
        
        # 每30秒检查一次时间
        time.sleep(30)


def interactive_mode():
    """
    交互式模式 - 用户可以选择执行方式
    """
    print("🤖 通勤助手交互模式")
    print("请选择执行方式:")
    print("1. 立即执行一次检查")
    print("2. 设置定时执行")
    print("3. 测试配置")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        run_manual_check()
    elif choice == "2":
        print("\n设置定时执行时间:")
        try:
            hour = int(input("请输入小时 (0-23): "))
            minute = int(input("请输入分钟 (0-59): "))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                run_scheduled_check(hour, minute)
            else:
                print("❌ 时间格式错误!")
        except ValueError:
            print("❌ 请输入有效的数字!")
    elif choice == "3":
        test_configuration()
    else:
        print("❌ 无效选择!")


def test_configuration():
    """
    测试配置是否正确
    """
    print("🧪 配置测试模式")
    print("=" * 30)
    
    # 测试高德API Key
    print("1. 测试高德地图API...")
    if "your_" in AMAP_API_KEY.lower():
        print("❌ 请先填写高德API Key!")
    else:
        print("✅ 高德API Key已配置")
        # 可以添加实际的API测试
    
    # 测试钉钉配置
    print("\n2. 测试钉钉配置...")
    if "your_" in DINGTALK_WEBHOOK.lower():
        print("❌ 请先填写钉钉Webhook URL!")
    else:
        print("✅ 钉钉Webhook已配置")
        # 可以添加实际的消息测试
    
    # 显示配置信息
    print(f"\n📋 当前配置:")
    print(f"   出发地: {HOME_LOCATION}")
    print(f"   目的地: {WORK_LOCATION}")
    print(f"   钉钉加签: {'已配置' if DINGTALK_SECRET and 'your_' not in DINGTALK_SECRET.lower() else '未配置'}")


def show_help():
    """
    显示帮助信息
    """
    help_text = """
📖 通勤助手使用说明

【快速开始】
1. 获取高德API Key: https://lbs.amap.com/
2. 创建钉钉群机器人: 群设置 → 智能群助手 → 添加机器人
3. 在上方配置区域填写相关信息
4. 运行程序即可

【运行方式】
- 直接运行: python commute_assistant.py
- 命令行参数:
  python commute_assistant.py --manual    # 手动执行
  python commute_assistant.py --test       # 测试配置
  python commute_assistant.py --schedule   # 定时模式

【配置说明】
- 坐标格式: "经度,纬度" (如: "116.481485,39.990464")
- 获取坐标: 在高德地图网页版右键点击位置
- API Key: 高德开放平台免费申请
- Webhook: 钉钉群机器人自动生成
"""
    print(help_text)


def main():
    """
    主函数 - 程序入口
    """
    import sys
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "--manual":
            run_manual_check()
        elif mode == "--test":
            test_configuration()
        elif mode == "--schedule":
            run_scheduled_check()  # 默认8:30
        elif mode == "--help":
            show_help()
        else:
            print(f"❌ 未知参数: {mode}")
            show_help()
    else:
        # 默认交互模式
        interactive_mode()


if __name__ == "__main__":
    print("🚗 智能通勤助手 (Dumb模式)")
    print("最简单的一站式通勤提醒解决方案")
    print()
    
    # 检查基本配置
    if ("your_" in AMAP_API_KEY.lower() or 
        "your_" in DINGTALK_WEBHOOK.lower()):
        print("⚠️  检测到未完成的配置!")
        print("💡 请先在文件顶部的配置区域填写相关信息")
        print()
        test_configuration()
    else:
        main()