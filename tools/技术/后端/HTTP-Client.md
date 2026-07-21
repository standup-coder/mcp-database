# 🌐 HTTP Client MCP

> 分类：技术 / 后端
> 底层：httpx / aiohttp
> 适用场景：调用任意 HTTP API、集成第三方服务、调试接口

---

## 一、简介

HTTP Client MCP 是**最通用**的 MCP —— 只要是 HTTP 接口，理论上都能调。
LLM 可以构造任意请求（GET / POST / PUT / DELETE / PATCH），带 Header、带 Cookie、带鉴权。

> 默认工具数：5

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 任意方法 | GET / POST / PUT / PATCH / DELETE / HEAD / OPTIONS |
| 自定义 Header | 任意 Header，含鉴权 |
| 请求体 | JSON / form / multipart / 原始文本 |
| 鉴权 | Bearer / Basic / API Key / 自定义 |
| 代理 | HTTP / SOCKS |
| 响应解析 | 自动 JSON / 原始文本 / 二进制 |

---

## 三、配置

### 3.1 全局配置

```bash
# 可选：默认超时（秒）
HTTP_DEFAULT_TIMEOUT=30

# 可选：最大响应体（字节）
HTTP_MAX_RESPONSE_SIZE=10485760      # 10MB

# 可选：默认 User-Agent
HTTP_USER_AGENT=MCP-HTTP-Client/1.0

# 可选：代理（企业内网）
# HTTP_PROXY=http://proxy.company.com:8080

# 可选：是否跟随重定向
HTTP_FOLLOW_REDIRECTS=true

# 可选：最大重定向次数
HTTP_MAX_REDIRECTS=5

# 可选：SSL 校验（自签证书环境关掉）
HTTP_VERIFY_SSL=true
```

### 3.2 域名白名单（强烈推荐）

```bash
# 限制只能访问这些域名
HTTP_ALLOWED_HOSTS=api.github.com,api.openai.com,*.amap.com,oapi.dingtalk.com

# 黑名单（比白名单更严格）
# HTTP_BLOCKED_HOSTS=localhost,127.0.0.1,*.internal
```

> ⚠️ **没配白名单 = 可以访问任意内网**（包括 metadata、内网服务），SSRF 风险！

### 3.3 内网 / SSRF 防护

```bash
# 禁止访问的 IP 段
HTTP_BLOCKED_IPS=127.0.0.0/8,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.0.0/16
```

---

## 四、使用示例

### 4.1 GET 请求

```bash
curl -X POST http://localhost:8000/mcp/execute/http_client/request \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "https://api.github.com/repos/python/cpython",
    "headers": {
      "Accept": "application/vnd.github+json",
      "Authorization": "Bearer ghp_xxx"
    }
  }'
```

### 4.2 POST JSON

```bash
curl -X POST http://localhost:8000/mcp/execute/http_client/request \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "https://api.openai.com/v1/chat/completions",
    "headers": {
      "Authorization": "Bearer sk-xxx",
      "Content-Type": "application/json"
    },
    "body": {
      "model": "gpt-4o-mini",
      "messages": [{"role": "user", "content": "Hello"}]
    }
  }'
```

### 4.3 表单提交

```bash
curl -X POST http://localhost:8000/mcp/execute/http_client/request \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "https://example.com/login",
    "form": {
      "username": "alice",
      "password": "xxx"
    }
  }'
```

### 4.4 文件上传

```bash
curl -X POST http://localhost:8000/mcp/execute/http_client/request \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "POST",
    "url": "https://api.example.com/upload",
    "multipart": {
      "file": "/local/path/to/file.png",
      "category": "avatar"
    }
  }'
```

---

## 五、典型使用流程

### 场景：调用三方 SaaS API

```text
 业务需求        LLM           HTTP Client MCP        三方 API
   │              │                  │                  │
   │ "调通        │                  │                  │
   │  极光推送"   │                  │                  │
   ├─────────────▶│                  │                  │
   │              │  POST /messages  │                  │
   │              ├─────────────────▶│                  │
   │              │                  │  域名白名单校验  │
   │              │                  │  ✅ api.jpush.cn│
   │              │                  │                  │
   │              │                  │  HTTPS POST     │
   │              │                  │  + Auth Header  │
   │              │                  ├─────────────────▶│
   │              │                  │◀─────────────────┤
   │              │                  │  200 OK          │
   │              │                  │  msg_id: 123    │
   │              │◀─────────────────┤                  │
   │ "推送成功"   │                  │                  │
   │◀─────────────┤                  │                  │
```

### 场景：通用 Webhook 接收 + 转发

```text
 GitHub        FastAPI        HTTP Client       下游服务
 (PR 事件)      (webhook)          │                │
    │             │                │                │
    │  push       │                │                │
    ├────────────▶│                │                │
    │             │  触发回调      │                │
    │             ├───────────────▶│                │
    │             │                │  转发到内部    │
    │             │                ├───────────────▶│
    │             │                │                │
    │             │                │  (审计: URL,   │
    │             │                │   状态码,      │
    │             │                │   耗时)        │
    │             │                │                │
    │             │  200 OK        │                │
    │◀────────────┤                │                │
```

### 场景：SSRF 防护流程

```text
  LLM            HTTP Client MCP            内网
   │                 │                       │
   │  GET http://10.x.x.x                  │
   ├────────────────▶│                       │
   │                 │  1. 域名/IP 检查      │
   │                 │  ❌ 10.0.0.0/8 黑名单 │
   │                 │                       │
   │                 │  拒绝 + 告警          │
   │                 ├──────────────────────▶│
   │ "403 Forbidden: │
   │  blocked IP"   │                       │
   │◀────────────────┤                       │
```

---

## 六、SSRF 安全建议

**SSRF（Server-Side Request Forgery）** 是 HTTP Client 最大的安全风险。LLM 可能会被诱导访问内网服务。

防护清单：

| 措施 | 说明 |
|------|------|
| **域名白名单** | 只允许必要的外网域名 |
| **IP 黑名单** | 禁止 10/8、172.16/12、192.168/16、169.254/16 等内网段 |
| **DNS 解析检查** | 防止域名解析到内网 IP（需要在调用前解析一次） |
| **协议限制** | 只允许 http/https，禁止 file://、gopher:// 等 |
| **响应大小限制** | `HTTP_MAX_RESPONSE_SIZE` 防止读大文件拖慢服务 |
| **审计日志** | 记录所有请求 URL + 响应码 |

---

## 六、注意事项

- **超时**：默认 30 秒，慢接口调大
- **大文件下载**：用 stream 模式，避免一次性读进内存
- **Cookie 持久化**：HTTP Client 默认不持久化 Cookie；需要登录态的接口用专门的 MCP
- **重试**：框架默认不重试；如果需要，用业务层包一层
- **编码**：响应体自动按 charset 解码；JSON 失败时返回原文

---

## 七、相关工具

- [GitHub](../运维/GitHub.md) - 调 GitHub API 也可以直接用这个
- [Database](./Database.md) - 多数 SaaS 平台有 HTTP API 可替代直接连库
- [Brave Search](../知识库/Brave-Search.md) - 公开网页数据也可以走 HTTP Client
