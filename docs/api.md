# API接口文档

## 概述

MCP Commute Assistant API 提供了完整的通勤信息服务接口，支持路线查询、定时任务管理和系统监控等功能。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API版本**: v1.0.0
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

## 认证方式

当前版本API无需认证，但在生产环境中建议添加API密钥认证。

## 错误响应格式

```json
{
  "error": "错误描述",
  "detail": "详细错误信息",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## API端点详解

### 1. 健康检查

#### GET `/health`

检查服务健康状态

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "checks": {
    "amap_api": {
      "status": "healthy",
      "response_time": "normal"
    },
    "dingtalk_api": {
      "status": "healthy"
    }
  }
}
```

### 2. 通勤检查

#### POST `/commute/check`

手动触发通勤检查任务

**请求示例:**
```bash
curl -X POST http://localhost:8000/commute/check
```

**响应示例:**
```json
{
  "message": "通勤检查任务已启动",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 3. 任务状态查询

#### GET `/commute/status/{task_id}`

查询指定任务的执行状态

**路径参数:**
- `task_id` (string, required): 任务ID

**响应示例:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "SUCCESS",
  "result": {
    "status": "success",
    "timestamp": "2024-01-01T12:05:00.000Z",
    "route_info": {
      "distance": 15000,
      "duration": 1800,
      "traffic_lights": 8
    },
    "notification_sent": true
  },
  "timestamp": "2024-01-01T12:05:01.000Z"
}
```

**状态说明:**
- `PENDING`: 任务等待执行
- `STARTED`: 任务正在执行
- `SUCCESS`: 任务执行成功
- `FAILURE`: 任务执行失败
- `REVOKED`: 任务被撤销

### 4. 配置信息（开发环境）

#### GET `/config/info`

获取当前配置信息（仅开发环境可用）

**响应示例:**
```json
{
  "config": {
    "app_env": "development",
    "debug": true,
    "log_level": "DEBUG",
    "amap_origin": "116.481485,39.990464",
    "amap_destination": "116.481485,39.990464",
    "redis_host": "localhost",
    "redis_port": 6379
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### 5. 测试通知（开发环境）

#### POST `/test/notification`

发送测试通知消息（仅开发环境可用）

**响应示例:**
```json
{
  "message": "测试通知发送成功",
  "result": {
    "errcode": 0,
    "errmsg": "ok",
    "msgid": "test_message_id"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## WebSocket支持（可选）

### 实时通知订阅

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到通知:', data);
};

ws.onopen = function(event) {
    console.log('WebSocket连接已建立');
};
```

## SDK使用示例

### Python客户端

```python
import requests
import time

class CommuteAssistantClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def check_health(self):
        """检查服务健康状态"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def trigger_commute_check(self):
        """触发通勤检查"""
        response = requests.post(f"{self.base_url}/commute/check")
        return response.json()
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        response = requests.get(f"{self.base_url}/commute/status/{task_id}")
        return response.json()
    
    def wait_for_completion(self, task_id, timeout=300):
        """等待任务完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            if status['status'] in ['SUCCESS', 'FAILURE']:
                return status
            time.sleep(5)
        raise TimeoutError("任务执行超时")

# 使用示例
client = CommuteAssistantClient()

# 检查健康状态
health = client.check_health()
print(f"服务状态: {health['status']}")

# 触发通勤检查
result = client.trigger_commute_check()
task_id = result['task_id']
print(f"任务ID: {task_id}")

# 等待任务完成
final_status = client.wait_for_completion(task_id)
print(f"最终状态: {final_status['status']}")
```

### JavaScript客户端

```javascript
class CommuteAssistantClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async checkHealth() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
    
    async triggerCommuteCheck() {
        const response = await fetch(`${this.baseUrl}/commute/check`, {
            method: 'POST'
        });
        return await response.json();
    }
    
    async getTaskStatus(taskId) {
        const response = await fetch(`${this.baseUrl}/commute/status/${taskId}`);
        return await response.json();
    }
    
    async waitForCompletion(taskId, timeout = 300000) {
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
            const status = await this.getTaskStatus(taskId);
            if (['SUCCESS', 'FAILURE'].includes(status.status)) {
                return status;
            }
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
        throw new Error('任务执行超时');
    }
}

// 使用示例
const client = new CommuteAssistantClient();

async function main() {
    try {
        // 检查健康状态
        const health = await client.checkHealth();
        console.log('服务状态:', health.status);
        
        // 触发通勤检查
        const result = await client.triggerCommuteCheck();
        const taskId = result.task_id;
        console.log('任务ID:', taskId);
        
        // 等待任务完成
        const finalStatus = await client.waitForCompletion(taskId);
        console.log('最终状态:', finalStatus.status);
        
    } catch (error) {
        console.error('操作失败:', error);
    }
}

main();
```

## 限流和配额

为了保证服务稳定性，API实施以下限制：

- **健康检查**: 无限制
- **通勤检查**: 每小时最多10次
- **任务查询**: 每分钟最多60次
- **配置查询**: 仅开发环境，无限制

超过限制的请求将返回429状态码。

## 版本兼容性

当前API版本为v1.0.0，后续版本将保持向后兼容性。重大变更将在文档中明确标注。

## 联系和支持

如有问题，请提交Issue或联系项目维护者。