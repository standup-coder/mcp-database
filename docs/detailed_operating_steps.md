# 📋 详细操作步骤手册

本手册提供MCP4Coder每个功能的详细操作步骤，确保用户能够准确执行每一步操作。

## 🎯 第一部分：环境准备

### 1.1 系统环境检查

#### 检查Python版本
```bash
# Windows
python --version

# Linux/Mac
python3 --version

# 预期输出: Python 3.9.x 或更高版本
```

#### 检查Git安装
```bash
git --version
# 预期输出: git version 2.x.x
```

#### 检查Docker安装（专业模式需要）
```bash
docker --version
docker-compose --version

# 预期输出:
# Docker version 20.x.x
# docker-compose version 1.29.x
```

### 1.2 项目获取

#### 方法一：Git克隆（推荐）
```bash
# 1. 创建项目目录
mkdir projects
cd projects

# 2. 克隆项目
git clone https://github.com/your-username/mcp4coder.git

# 3. 进入项目目录
cd mcp4coder
```

#### 方法二：直接下载
```bash
# 1. 访问GitHub页面
# https://github.com/your-username/mcp4coder

# 2. 点击"Code" → "Download ZIP"

# 3. 解压到目标目录
unzip mcp4coder-main.zip
cd mcp4coder-main
```

## 🎯 第二部分：配置获取详解

### 2.1 高德地图API配置

#### 步骤1：注册高德开放平台账号
```
1. 访问: https://lbs.amap.com/
2. 点击右上角"注册"
3. 填写手机号码和验证码
4. 完善个人信息
5. 完成邮箱验证
```

#### 步骤2：创建应用
```
1. 登录控制台
2. 左侧菜单选择"应用管理" → "我的应用"
3. 点击"创建新应用"
4. 填写应用信息:
   - 应用名称: MCP通勤助手
   - 应用类型: Web服务
   - 应用描述: 通勤路线查询和通知
5. 点击"创建"
```

#### 步骤3：获取API Key
```
1. 在应用列表中找到刚创建的应用
2. 点击"添加" → "Key"
3. 选择服务平台: Web服务
4. 填写备注信息
5. 点击"提交"
6. 复制生成的API Key
```

#### 步骤4：验证API Key有效性
```bash
# 测试API调用
curl "https://restapi.amap.com/v3/direction/driving?key=YOUR_API_KEY&origin=116.481485,39.990464&destination=116.436795,39.974805"

# 成功响应示例:
{
  "status": "1",
  "info": "OK",
  "route": {
    "paths": [{
      "distance": "15000",
      "duration": "1800"
    }]
  }
}
```

### 2.2 钉钉机器人配置

#### 步骤1：创建群机器人
```
1. 打开钉钉客户端
2. 进入目标群聊
3. 点击右上角"群设置"
4. 选择"智能群助手"
5. 点击"添加机器人"
6. 选择"自定义机器人"
```

#### 步骤2：配置安全设置
```
安全设置选项:
□ 自定义关键词 (推荐新手)
  - 添加关键词: 通勤提醒

□ 加签 (推荐生产环境)
  - 复制生成的加签密钥

□ IP地址段 (企业环境)
  - 添加允许的IP段

□ 不开启任何安全设置 (不推荐)
```

#### 步骤3：获取配置信息
```
1. 机器人名称: 通勤助手
2. 复制Webhook URL:
   格式: https://oapi.dingtalk.com/robot/send?access_token=xxxxx
3. 如果选择了加签，复制密钥:
   格式: SECxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.3 坐标获取方法

#### 方法一：高德地图网页版
```bash
# 1. 访问 https://ditu.amap.com/
# 2. 搜索地点名称或直接点击地图
# 3. 右键点击精确位置
# 4. 选择"复制坐标"
# 5. 得到格式: 116.481485,39.990464
```

#### 方法二：手机高德地图
```
1. 打开高德地图APP
2. 长按地图上的位置点
3. 点击底部弹出的信息框
4. 选择"复制坐标"
```

#### 方法三：坐标验证
```python
# 验证坐标的Python脚本
def validate_coordinates(coord_str):
    try:
        lon, lat = coord_str.split(',')
        lon_float = float(lon)
        lat_float = float(lat)
        
        # 经纬度范围检查
        if -180 <= lon_float <= 180 and -90 <= lat_float <= 90:
            print(f"✓ 坐标有效: 经度{lon_float}, 纬度{lat_float}")
            return True
        else:
            print("✗ 坐标超出有效范围")
            return False
    except:
        print("✗ 坐标格式错误")
        return False

# 测试
validate_coordinates("116.481485,39.990464")  # 应该返回True
```

## 🎯 第三部分：Dumb模式详细配置

### 3.1 文件编辑步骤

#### 步骤1：定位配置文件
```bash
# 确认当前位置
pwd  # Linux/Mac
cd   # Windows

# 进入dumb模式目录
cd dumb_mode

# 确认文件存在
ls commute_assistant.py  # Linux/Mac
dir commute_assistant.py # Windows
```

#### 步骤2：备份原始文件
```bash
# 创建备份
cp commute_assistant.py commute_assistant.py.backup
```

#### 步骤3：编辑配置
使用任一文本编辑器：

**Windows记事本:**
```bash
notepad commute_assistant.py
```

**VS Code:**
```bash
code commute_assistant.py
```

**Vim (Linux/Mac):**
```bash
vim commute_assistant.py
```

#### 步骤4：修改配置区域
找到文件中的配置区域：

```python
# ==================== 配置区域（示例）====================

# 高德地图配置
AMAP_API_KEY = "在这里粘贴你的高德API Key"  # ← 修改这里
HOME_LOCATION = "在这里粘贴家的坐标"         # ← 修改这里
WORK_LOCATION = "在这里粘贴公司的坐标"       # ← 修改这里

# 钉钉配置
DINGTALK_WEBHOOK = "在这里粘贴钉钉Webhook URL"  # ← 修改这里
DINGTALK_SECRET = "如果有加签密钥就填写"        # ← 修改这里

# ======================================================
```

### 3.2 配置验证

#### 步骤1：语法检查
```bash
# 检查Python语法
python -m py_compile commute_assistant.py

# 如果没有输出，说明语法正确
```

#### 步骤2：配置测试
```bash
# 运行配置测试
python commute_assistant.py --test

# 预期输出:
# 🧪 配置测试模式
# ==============================
# 1. 测试高德地图API...
# ✅ 高德API Key已配置
# 2. 测试钉钉配置...
# ✅ 钉钉Webhook已配置
```

## 🎯 第四部分：专业模式详细配置

### 4.1 环境变量配置

#### 步骤1：创建环境文件
```bash
# 复制模板
cp .env.example .env

# 验证文件创建
ls -la .env
```

#### 步骤2：编辑环境变量
```bash
# 使用编辑器打开
nano .env
# 或
vim .env
```

#### 步骤3：填写完整配置
```bash
# 应用配置
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# 高德地图API配置
AMAP_API_KEY=your_actual_amap_api_key_here
AMAP_ORIGIN=116.481485,39.990464
AMAP_DESTINATION=116.436795,39.974805
AMAP_STRATEGY=0

# 钉钉机器人配置
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=your_token_here
DINGTALK_SECRET=your_secret_here
DINGTALK_KEYWORD=通勤提醒

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Celery配置
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CELERY_TIMEZONE=Asia/Shanghai

# 定时任务配置
COMMUTE_CHECK_CRON=0 30 8 * * *
```

### 4.2 虚拟环境配置

#### 步骤1：创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 验证创建成功
ls venv/
```

#### 步骤2：激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 验证激活
which python  # 应该指向venv目录下的python
```

#### 步骤3：安装依赖
```bash
# 安装生产依赖
pip install -r requirements-prod.txt

# 或安装完整开发依赖
pip install -r requirements.txt

# 验证安装
pip list | grep fastapi
```

## 🎯 第五部分：服务启动和验证

### 5.1 Dumb模式运行

#### 方式1：交互式运行
```bash
# 启动程序
python commute_assistant.py

# 程序输出示例:
# 🚗 智能通勤助手 (Dumb模式)
# 最简单的一站式通勤提醒解决方案
# 
# 🤖 通勤助手交互模式
# 请选择执行方式:
# 1. 立即执行一次检查
# 2. 设置定时执行
# 3. 测试配置
# 
# 请输入选择 (1/2/3): 
```

#### 方式2：命令行参数运行
```bash
# 测试配置
python commute_assistant.py --test

# 立即执行
python commute_assistant.py --manual

# 定时执行
python commute_assistant.py --schedule

# 查看帮助
python commute_assistant.py --help
```

### 5.2 专业模式运行

#### 步骤1：启动Docker服务
```bash
# 启动所有服务
docker-compose up -d

# 查看启动进度
docker-compose logs -f

# 验证服务状态
docker-compose ps
```

#### 步骤2：验证服务运行
```bash
# 检查健康状态
curl http://localhost:8000/health

# 检查API文档
curl http://localhost:8000/docs

# 查看应用日志
docker-compose logs -f app
```

#### 步骤3：测试核心功能
```bash
# 触发通勤检查任务
curl -X POST http://localhost:8000/api/tasks/trigger-commute-check

# 查看任务执行结果
curl http://localhost:8000/api/tasks/latest-result

# 查看系统指标
curl http://localhost:8000/metrics
```

## 🎯 第六部分：故障排除详细步骤

### 6.1 网络连接问题

#### 诊断步骤：
```bash
# 1. 检查网络连通性
ping www.baidu.com

# 2. 检查目标服务可达性
telnet restapi.amap.com 443
telnet oapi.dingtalk.com 443

# 3. 检查DNS解析
nslookup restapi.amap.com
nslookup oapi.dingtalk.com

# 4. 测试HTTPS连接
curl -I https://restapi.amap.com
curl -I https://oapi.dingtalk.com
```

#### 解决方案：
```bash
# 如果是国内网络，可能需要配置代理
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 或者检查防火墙设置
sudo ufw status  # Ubuntu
```

### 6.2 配置错误排查

#### 配置验证脚本：
```python
#!/usr/bin/env python3
# config_validator.py

import os
import sys
from urllib.parse import urlparse

def validate_env_config():
    """验证环境变量配置"""
    required_vars = [
        'AMAP_API_KEY',
        'AMAP_ORIGIN', 
        'AMAP_DESTINATION',
        'DINGTALK_WEBHOOK_URL'
    ]
    
    errors = []
    
    # 检查必需变量
    for var in required_vars:
        value = os.getenv(var, '')
        if not value or 'your_' in value:
            errors.append(f"缺少或未配置: {var}")
    
    # 检查API Key格式
    api_key = os.getenv('AMAP_API_KEY', '')
    if api_key and len(api_key) != 32:
        errors.append("API Key长度不正确，应为32位字符")
    
    # 检查坐标格式
    origin = os.getenv('AMAP_ORIGIN', '')
    dest = os.getenv('AMAP_DESTINATION', '')
    
    for coord_name, coord_value in [('起点', origin), ('终点', dest)]:
        if coord_value:
            try:
                lon, lat = map(float, coord_value.split(','))
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    errors.append(f"{coord_name}坐标超出有效范围")
            except:
                errors.append(f"{coord_name}坐标格式错误")
    
    # 检查Webhook URL
    webhook = os.getenv('DINGTALK_WEBHOOK_URL', '')
    if webhook:
        try:
            parsed = urlparse(webhook)
            if not (parsed.scheme and parsed.netloc):
                errors.append("Webhook URL格式不正确")
        except:
            errors.append("Webhook URL解析失败")
    
    return errors

if __name__ == "__main__":
    errors = validate_env_config()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ 配置验证通过")
        sys.exit(0)
```

### 6.3 日志分析步骤

#### 查看不同层级日志：
```bash
# 应用日志
tail -f logs/app.log

# Docker容器日志
docker-compose logs -f app
docker-compose logs -f redis

# 系统日志（Linux）
journalctl -u docker -f

# 错误日志筛选
grep "ERROR" logs/app.log
grep "Exception" logs/app.log
```

#### 日志级别调整：
```bash
# 临时提高日志级别
export LOG_LEVEL=DEBUG
python commute_assistant.py

# 或在代码中修改
# 将 loguru logger 的 level 改为 "DEBUG"
```

## 🎯 第七部分：维护和监控

### 7.1 定期健康检查
```bash
# 运行健康检查脚本
python scripts/health_check.py

# 设置定时检查（Linux crontab）
# 每小时检查一次
0 * * * * cd /path/to/mcp4coder && python scripts/health_check.py >> /var/log/mcp4coder-health.log 2>&1
```

### 7.2 性能监控
```bash
# 查看系统资源使用
htop  # Linux
top   # Mac/Windows

# 查看Docker资源使用
docker stats

# 查看应用性能指标
curl http://localhost:8000/metrics
```

### 7.3 数据备份
```bash
# 备份配置文件
cp .env .env.backup.$(date +%Y%m%d)

# 备份日志文件
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# 备份整个项目
tar -czf mcp4coder-backup-$(date +%Y%m%d).tar.gz --exclude='venv' --exclude='__pycache__' .
```

---

🎯 **完成！** 按照这些详细步骤，您应该能够成功部署和运行MCP4Coder。
如果遇到任何问题，请参考对应的故障排除章节或寻求技术支持。