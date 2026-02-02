# 🚀 快速开始完整指南

这份指南将帮助您在30分钟内完成MCP4Coder的安装和配置。

## 🎯 选择适合您的使用模式

### 🎯 新手用户推荐：Dumb模式
- ✅ 无需编程基础
- ✅ 5分钟快速上手
- ✅ 详细中文提示
- ✅ 一个文件搞定

### 🏢 开发者推荐：专业模式
- ✅ 完整MCP协议支持
- ✅ 可扩展架构设计
- ✅ 企业级监控系统
- ✅ 可视化工作流设计

## 🎯 Dumb模式快速开始 (5分钟)

### 步骤1：准备工作 (1分钟)

```bash
# 克隆项目
git clone https://github.com/your-username/mcp4coder.git
cd mcp4coder/dumb_mode

# 安装最小依赖 (只有1个包!)
pip install requests
```

### 步骤2：获取配置信息 (2分钟)

#### 📍 获取高德API Key
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册账号 → 控制台 → 应用管理 → 创建新应用
3. 选择"Web服务" → 获取API Key

#### 🤖 创建钉钉机器人
1. 打开钉钉 → 选择工作群
2. 群设置 → 智能群助手 → 添加机器人
3. 选择"自定义机器人" → 完成安全设置
4. 复制Webhook URL

#### 🌍 获取坐标
1. 打开 [高德地图](https://ditu.amap.com/)
2. 右键点击家的位置 → 复制坐标
3. 右键点击公司位置 → 复制坐标
4. 格式应为："经度,纬度" (如："116.481485,39.990464")

### 步骤3：配置和运行 (2分钟)

#### 编辑配置文件
用任意文本编辑器打开 `commute_assistant.py`，找到配置区域：

```python
# ==================== 配置区域 ====================

# 高德地图配置 (必填)
AMAP_API_KEY = "在这里粘贴你的高德API Key"
HOME_LOCATION = "在这里粘贴家的坐标"      # 如: "116.481485,39.990464"
WORK_LOCATION = "在这里粘贴公司的坐标"    # 如: "116.436795,39.974805"

# 钉钉配置 (必填)
DINGTALK_WEBHOOK = "在这里粘贴钉钉Webhook URL"
DINGTALK_SECRET = "如果有加签密钥就填写，没有就留空"

# =================================================
```

#### 运行程序
```bash
# 方式1：交互式运行 (推荐)
python commute_assistant.py

# 方式2：直接测试配置
python commute_assistant.py --test

# 方式3：立即执行一次
python commute_assistant.py --manual
```

### 成功运行示例
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

📍 查询路线: 116.481485,39.990464 → 116.436795,39.974805
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

## 🏢 专业模式快速开始 (15分钟)

### 步骤1：环境准备 (3分钟)

```bash
# 系统要求
# - Python 3.9+
# - Docker & Docker Compose
# - Git

# 克隆项目
git clone https://github.com/your-username/mcp4coder.git
cd mcp4coder

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤2：配置环境变量 (3分钟)

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

在 `.env` 文件中填写必要配置：

```bash
# 高德地图API配置
AMAP_API_KEY=your_actual_amap_api_key_here
AMAP_ORIGIN=116.481485,39.990464
AMAP_DESTINATION=116.436795,39.974805

# 钉钉机器人配置
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=your_token_here
DINGTALK_SECRET=your_secret_here

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 步骤3：启动服务 (5分钟)

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 等待服务启动完成 (约1-2分钟)
# 查看启动日志
docker-compose logs -f app
```

### 步骤4：验证运行 (4分钟)

```bash
# 1. 检查健康状态
curl http://localhost:8000/health

# 期望输出:
{
  "status": "healthy",
  "timestamp": "2024-01-01T08:30:00",
  "system_metrics": {...}
}

# 2. 触发测试任务
curl -X POST http://localhost:8000/api/tasks/trigger-commute-check

# 3. 查看执行结果
curl http://localhost:8000/api/tasks/latest-result
```

## 🎮 不同使用场景的操作指南

### 场景1：每天定时检查

#### Dumb模式
```bash
# 设置每天早上8:30自动执行
python commute_assistant.py --schedule

# 或者在程序中选择定时执行模式
```

#### 专业模式
```bash
# 服务已内置定时任务，默认每天8:30执行
# 可通过环境变量调整时间:
# COMMUTE_CHECK_CRON=0 30 8 * * *
```

### 场景2：临时测试路线

#### Dumb模式
```bash
# 立即执行一次检查
python commute_assistant.py --manual
```

#### 专业模式
```bash
# 手动触发任务
curl -X POST http://localhost:8000/api/tasks/trigger-commute-check
```

### 场景3：修改通勤路线

#### Dumb模式
```bash
# 直接编辑 commute_assistant.py 中的坐标
HOME_LOCATION = "新的家坐标"
WORK_LOCATION = "新的公司坐标"
```

#### 专业模式
```bash
# 修改 .env 文件中的坐标配置
# 然后重启服务
docker-compose restart app
```

## 🔧 常见问题快速解决

### 问题1：API Key无效
```bash
# 验证API Key
curl "https://restapi.amap.com/v3/direction/driving?key=YOUR_KEY&origin=116,39&destination=116,39"

# 如果返回错误，检查：
# 1. API Key是否正确复制
# 2. 是否为Web服务类型的Key
# 3. 是否超出调用次数限制
```

### 问题2：钉钉消息发送失败
```bash
# 检查Webhook URL格式
# 应该是: https://oapi.dingtalk.com/robot/send?access_token=xxx

# 如果有加签，确保secret正确
# 如果没有加签，DINGTALK_SECRET可以留空
```

### 问题3：坐标格式错误
```bash
# 正确格式: "经度,纬度"
# 注意事项:
# 1. 使用英文逗号分隔
# 2. 不要有空格
# 3. 经纬度顺序不能颠倒
# 4. 小数点后位数建议6位
```

### 问题4：Docker容器无法启动
```bash
# 查看详细错误信息
docker-compose logs app

# 常见解决方案:
# 1. 检查端口是否被占用: netstat -an | grep 8000
# 2. 重新构建镜像: docker-compose up --build
# 3. 清理旧容器: docker-compose down -v
```

## 📱 移动端使用

### Termux (Android)
```bash
# 安装Termux后执行:
pkg update
pkg install python git
git clone https://github.com/your-username/mcp4coder.git
cd mcp4coder/dumb_mode
pip install requests
# 然后按上面的步骤配置和运行
```

### Pythonista (iOS)
```
1. 在App Store下载Pythonista
2. 创建新脚本
3. 复制commute_assistant.py的内容
4. 安装requests库
5. 填写配置信息并运行
```

## 🎯 进阶使用技巧

### 1. 多条路线监控
```python
# 在dumb模式中可以创建多个检查函数
def check_home_to_gym():
    route_info = get_route_time("家坐标", "健身房坐标", AMAP_API_KEY)
    send_commute_notification("健身群webhook", route_info)

def check_office_to_client():
    route_info = get_route_time("办公室坐标", "客户坐标", AMAP_API_KEY)
    send_commute_notification("工作群webhook", route_info)
```

### 2. 自定义通知内容
```python
# 修改simple_dingtalk.py中的消息模板
message = f"""🚗 个性化通勤提醒

📍 出发地: 家
📍 目的地: 公司
⏰ 当前时间: {time_str}
⏱️ 预计用时: {duration}分钟
📏 距离: {distance}公里
🚦 实时路况: 畅通

💼 祝您工作顺利!"""
```

### 3. 添加日志记录
```python
import logging
logging.basicConfig(filename='commute.log', level=logging.INFO)

# 在关键步骤添加日志
logging.info(f"开始查询路线: {origin} → {destination}")
logging.info(f"路线查询结果: {route_info}")
```

## 🆘 获取帮助

### 在线资源
- 📖 [完整文档](docs/)
- 🐛 [问题反馈](https://github.com/your-username/mcp4coder/issues)
- 💬 [社区讨论](https://github.com/your-username/mcp4coder/discussions)

### 本地调试
```bash
# 运行健康检查脚本
python scripts/health_check.py

# 查看详细日志
tail -f logs/app.log
```

---

🎯 **恭喜！您现在已经掌握了MCP4Coder的基本使用方法。**
如有任何问题，请随时查阅详细文档或寻求社区帮助。