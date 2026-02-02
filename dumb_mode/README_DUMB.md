# 🚗 Dumb模式 - 小白通勤助手

最简单的一站式通勤提醒解决方案，**零基础也能5分钟上手**！

## 🌟 特点

- ✅ **超级简单** - 只需填写几个配置项
- ✅ **一个文件** - 所有功能都在一个Python文件里
- ✅ **零依赖** - 只需要最基本的requests库
- ✅ **多种模式** - 手动执行、定时执行、交互模式
- ✅ **详细提示** - 每一步都有中文说明

## 🚀 快速开始 (5分钟搞定)

### 1. 准备工作

```bash
# 克隆项目
git clone https://github.com/your-username/mcp4coder.git
cd mcp4coder/dumb_mode

# 安装依赖 (只有requests一个包!)
pip install -r requirements.txt
```

### 2. 获取必要配置

**📌 高德地图API Key**
- 访问: https://lbs.amap.com/
- 注册账号并创建应用
- 获取Web服务API Key (免费!)

**📌 钉钉机器人**
- 打开钉钉 → 选择群聊
- 群设置 → 智能群助手 → 添加机器人
- 选择自定义机器人 → 获取Webhook URL

**📌 坐标获取**
- 打开高德地图网页版
- 右键点击起点/终点位置
- 复制坐标 (格式: 经度,纬度)

### 3. 配置信息

打开 `commute_assistant.py` 文件，找到配置区域：

```python
# ==================== 配置区域 ====================

# 高德地图配置
AMAP_API_KEY = "在这里填写你的高德API Key"
HOME_LOCATION = "116.481485,39.990464"      # 家的坐标
WORK_LOCATION = "116.481485,39.990464"     # 公司的坐标

# 钉钉配置
DINGTALK_WEBHOOK = "在这里填写你的钉钉Webhook URL"
DINGTALK_SECRET = "在这里填写钉钉加签密钥（可选）"

# =================================================
```

### 4. 运行程序

```bash
# 交互模式 (推荐新手)
python commute_assistant.py

# 手动执行一次
python commute_assistant.py --manual

# 测试配置
python commute_assistant.py --test

# 定时执行 (每天8:30)
python commute_assistant.py --schedule

# 查看帮助
python commute_assistant.py --help
```

## 🎯 使用示例

### 交互模式运行效果

```
🚗 智能通勤助手 (Dumb模式)
最简单的一站式通勤提醒解决方案

🤖 通勤助手交互模式
请选择执行方式:
1. 立即执行一次检查
2. 设置定时执行
3. 测试配置

请输入选择 (1/2/3): 1

==================================================
🚀 开始执行通勤检查...
==================================================
⏰ 当前时间: 2024-01-01 08:30:00

📍 查询路线: 116.481485,39.990464 → 116.481485,39.990464
📡 正在调用高德地图API...
路线查询成功!
距离: 15.0 公里
时长: 30 分钟

📊 路线详情:
   距离: 15.0 公里
   时长: 30分钟
   平均速度: 30.0 km/h

📤 准备发送钉钉通知...
钉钉消息发送成功!
✅ 通勤检查完成!
```

### 钉钉收到的消息样式

```
🚗 通勤路线提醒

出发时间: 08:30
预计行程: 30分钟
行驶距离: 15.0公里

祝您一路顺风! 🎯
```

## 📋 文件说明

```
dumb_mode/
├── commute_assistant.py    # 主程序文件 (一体化)
├── simple_amap.py          # 高德地图功能模块
├── simple_dingtalk.py      # 钉钉通知功能模块
├── requirements.txt        # 依赖包列表
├── README_DUMB.md         # 本说明文件
└── config_example.txt      # 配置示例文件
```

## ⚙️ 高级配置

### 修改定时时间

在 `commute_assistant.py` 中修改：

```python
# 原来的定时执行 (8:30)
run_scheduled_check(hour=8, minute=30)

# 修改为你想要的时间 (比如7:15)
run_scheduled_check(hour=7, minute=15)
```

### 添加多个路线

可以复制主函数创建多个检查函数：

```python
def check_home_to_gym():
    """检查家到健身房的路线"""
    route_info = get_route_time("家坐标", "健身房坐标", AMAP_API_KEY)
    send_commute_notification("另一个钉钉群webhook", route_info)

# 在main函数中调用
check_home_to_gym()
```

## ❓ 常见问题

### Q: 运行时报错"API Key无效"
A: 请检查高德API Key是否正确，确保是从Web服务API获取的Key

### Q: 钉钉消息发送失败
A: 检查Webhook URL是否正确，如果是加签机器人需要填写SECRET

### Q: 坐标格式不对
A: 坐标格式必须是 "经度,纬度"，注意是英文逗号，不要有空格

### Q: 如何后台运行
A: 在Linux/macOS上使用 `nohup python commute_assistant.py &`
   在Windows上可以使用任务计划程序

### Q: 如何开机自启动
A: 可以将程序添加到系统的启动项中，或者使用crontab (Linux) / 任务计划程序 (Windows)

## 🔧 故障排除

### 网络连接问题
```bash
# 测试网络连接
ping restapi.amap.com
ping oapi.dingtalk.com
```

### 依赖包问题
```bash
# 重新安装依赖
pip uninstall requests
pip install requests
```

### 权限问题
```bash
# Linux/macOS 给予执行权限
chmod +x commute_assistant.py
```

## 📱 移动端使用

程序可以在任何支持Python的设备上运行：
- 🖥️ Windows电脑
- 🍏 Mac电脑
- 🐧 Linux服务器
- 📱 Android手机 (Termux)
- 🍎 iPhone (Pythonista等)

## 🆘 技术支持

如果遇到问题：
1. 先运行 `python commute_assistant.py --test` 检查配置
2. 查看控制台输出的错误信息
3. 确保网络连接正常
4. 验证API Key和Webhook URL正确性

## 📄 许可证

MIT License - 可以自由使用和修改

---

<p align="center"> Made with ❤️ for Python beginners </p>