# -*- coding: utf-8 -*-
"""
简化版钉钉通知功能
最简单的小白模式 - 只需要Webhook URL就能发送消息
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime


def send_dingtalk_message(webhook_url, message_text, secret=None):
    """
    发送钉钉消息（最简版本）
    
    参数:
        webhook_url: 钉钉机器人的Webhook URL
        message_text: 要发送的消息内容
        secret: 钉钉机器人的加签密钥（可选）
    
    返回:
        bool: 发送是否成功
    """
    
    # 构造消息数据
    data = {
        "msgtype": "text",
        "text": {
            "content": message_text
        }
    }
    
    # 如果有加签密钥，需要生成签名
    headers = {'Content-Type': 'application/json'}
    url = webhook_url
    
    if secret:
        # 生成时间戳和签名
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        # 在URL中添加时间戳和签名参数
        url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
    
    try:
        # 发送POST请求
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(data),
            timeout=10
        )
        response.raise_for_status()
        
        # 解析返回结果
        result = response.json()
        
        # 检查发送是否成功
        if result.get('errcode') == 0:
            print("钉钉消息发送成功!")
            return True
        else:
            print(f"钉钉消息发送失败: {result.get('errmsg', '未知错误')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return False
    except Exception as e:
        print(f"发送消息时出现错误: {e}")
        return False


def send_commute_notification(webhook_url, commute_info, secret=None):
    """
    发送通勤通知消息
    
    参数:
        webhook_url: 钉钉Webhook URL
        commute_info: 通勤信息字典，包含distance_km和duration_minute
        secret: 加签密钥（可选）
    """
    
    # 获取当前时间
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    
    # 格式化通勤信息
    distance = commute_info.get('distance_km', 0)
    duration = commute_info.get('duration_minute', 0)
    
    # 构造通勤通知消息
    message = f"""🚗 通勤路线提醒
    
出发时间: {time_str}
预计行程: {duration}分钟
行驶距离: {distance}公里

祝您一路顺风! 🎯"""
    
    print("准备发送通勤通知...")
    print(f"消息内容:\n{message}")
    
    return send_dingtalk_message(webhook_url, message, secret)


def test_dingtalk_webhook():
    """
    测试钉钉Webhook功能
    """
    print("=== 钉钉消息发送测试 ===")
    
    # 这里需要替换为你的实际Webhook URL
    test_webhook = "https://oapi.dingtalk.com/robot/send?access_token=your_token_here"
    test_secret = "your_secret_here"  # 如果有加签，填写密钥
    
    # 测试消息
    test_message = "🔔 测试消息 - 系统运行正常"
    
    success = send_dingtalk_message(test_webhook, test_message, test_secret)
    
    if success:
        print("✅ 测试成功!")
    else:
        print("❌ 测试失败，请检查Webhook URL和网络连接")


# 便捷函数
def quick_send_message(webhook_url, content):
    """
    快速发送消息的简化函数
    """
    return send_dingtalk_message(webhook_url, content)


if __name__ == "__main__":
    test_dingtalk_webhook()