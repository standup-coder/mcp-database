# 🔗 Composio MCP（500+ 应用统一集成）

> 分类：技术 / 运维
> 官网：<https://composio.dev/>
> 适用场景：统一接入 500+ SaaS 应用、复杂工作流编排

---

## 一、简介

Composio 是**应用集成平台**，统一封装了 500+ 流行 SaaS：
- Slack / Notion / Linear / Jira / Asana
- Gmail / Outlook
- GitHub / GitLab
- Salesforce / HubSpot
- Google 全家桶（Sheets / Calendar / Drive / Docs）
- 等等

一个 Composio API Key 就能调用所有这些，省去单独维护一堆 Token / OAuth。

> 默认工具数：6

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 统一调用 | 同一 API 调不同应用 |
| OAuth 托管 | 帮你管用户授权 |
| 预建 Action | 500+ 应用的常用操作 |
| Trigger | 监听应用事件（webhook） |
| 工具集 | 按场景打包（Gmail 工具集 = 20 个工具） |
| 自定义 Action | 用代码扩展 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
COMPOSIO_API_KEY=ck_xxxxxxxxxxxxxxxx  # API Key
```

### 可选

```bash
COMPOSIO_DEFAULT_ENTITY_ID=default  # 默认 Entity
COMPOSIO_ENABLE_TRIGGERS=true  # 启用 Trigger
```

---

## 三、配置

### 3.1 申请 API Key

1. 打开 <https://composio.dev/>
2. 注册 → Dashboard → API Keys
3. 复制 Key

### 3.2 环境变量

```bash
# 必填
COMPOSIO_API_KEY=ck_xxxxxxxxxxxxxxxx

# 可选：默认 Entity（用户/工作区）
# COMPOSIO_DEFAULT_ENTITY_ID=default

# 可选：是否启用 Trigger
COMPOSIO_ENABLE_TRIGGERS=true
```

### 3.3 OAuth 授权

第一次调用某个应用时，Composio 会返回授权 URL，引导用户完成 OAuth。
之后所有调用都走 Composio，无需自己管理 Token。

---

## 四、使用示例

### 4.1 列出可用应用

```bash
curl -X POST http://localhost:8000/mcp/execute/composio/list_apps \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "productivity"
  }'
```

### 4.2 列出 Slack 的 Action

```bash
curl -X POST http://localhost:8000/mcp/execute/composio/list_actions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "slack"
  }'
```

### 4.3 执行 Action

```bash
curl -X POST http://localhost:8000/mcp/execute/composio/execute_action \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "slack",
    "action": "send_message",
    "params": {
      "channel": "#general",
      "text": "Hello from Composio!"
    }
  }'
```

### 4.4 Gmail 发送邮件

```bash
curl -X POST http://localhost:8000/mcp/execute/composio/execute_action \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "gmail",
    "action": "send_email",
    "params": {
      "to": "alice@company.com",
      "subject": "Weekly Report",
      "body": "本周数据：...",
      "html_body": "<h1>本周数据</h1><p>...</p>"
    }
  }'
```

### 4.5 Notion 创建页面

```bash
curl -X POST http://localhost:8000/mcp/execute/composio/execute_action \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "notion",
    "action": "create_page",
    "params": {
      "parent_id": "xxx",
      "title": "新页面",
      "children": [...]
    }
  }'
```

### 4.6 Trigger 监听

```bash
# 创建 trigger：监听 GitHub Issue
curl -X POST http://localhost:8000/mcp/execute/composio/create_trigger \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "github",
    "trigger": "new_issue",
    "config": {
      "owner": "my-org",
      "repo": "my-repo"
    },
    "webhook_url": "https://my-mcp.com/webhook"
  }'
```

---

## 五、典型使用流程

### 场景：新用户注册跨应用工作流

```text
 Stripe (新订阅)    Composio MCP           Gmail         HubSpot        Slack
     │                  │                    │              │              │
     │  trigger        │                    │              │              │
     │  new_subscription                  │              │              │
     ├─────────────────▶│                    │              │              │
     │                  │  编排 3 个 action │              │              │
     │                  │                    │              │              │
     │                  │  1. gmail.send    │              │              │
     │                  ├───────────────────▶│              │              │
     │                  │                    │  ✅ 邮件已发 │              │
     │                  │◀───────────────────┤              │              │
     │                  │                    │              │              │
     │                  │  2. hubspot.create_contact         │              │
     │                  ├───────────────────────────────────▶│              │
     │                  │                    │              │  ✅ 已建联系人│
     │                  │◀────────────────────────────────────┤              │
     │                  │                    │              │              │
     │                  │  3. slack.send    │              │              │
     │                  ├───────────────────────────────────────────────────▶│
     │                  │                    │              │     #sales    │
     │                  │                    │              │  ┌────────┐  │
     │                  │                    │              │  │🎉 新客户│  │
     │                  │                    │              │  │ ACME Inc│  │
     │                  │                    │              │  │ $999/月 │  │
     │                  │                    │              │  └────────┘  │
     │                  │                    │              │              │
     │  工作流完成     │                    │              │              │
     │◀─────────────────┤                    │              │              │
```

### 场景：替代多 MCP 维护

```text
         传统方式（5 个 MCP）              Composio 方式（1 个）
         ─────────────────────            ─────────────────────
         ┌─────────────┐                  ┌─────────────┐
         │ Slack MCP   │                  │             │
         │ Notion MCP  │                  │             │
         │ Linear MCP  │                  │  Composio   │
         │ GitHub MCP  │                  │  MCP        │
         │ Gmail MCP   │                  │  (1 个 Key) │
         └─────────────┘                  └─────────────┘
         5 个 Token                         1 个 Token
         5 套 OAuth                         Composio 统一管
         5 套权限配置                       500+ 应用按需开
         升级要改 5 个服务                  加新应用零配置
```

### 场景：自定义 Action 扩展

```text
 LLM            Composio MCP          后端
  │                 │                  │
  │  没有现成的    │                  │
  │  "发飞书消息"  │                  │
  │  Action       │                  │
  │                 │                  │
  │  create_custom_action              │
  │  app: feishu   │                  │
  │  code: Python  │                  │
  │  params: webhook_url, text         │
  ├────────────────▶│                  │
  │                 │  部署到沙箱     │
  │                 ├─────────────────▶│
  │                 │  ✅ Action ready │
  │                 │◀─────────────────┤
  │                 │                  │
  │  execute_action│                  │
  │  feishu.send  │                  │
  ├────────────────▶│                  │
  │                 │  调自定义 code  │
  │                 ├─────────────────▶│
```

### 5.2 替代单独维护一堆 MCP

如果项目需要：
- Slack + Notion + Linear + GitHub + Gmail
- 每个都单独维护一个 MCP = 5 个 Token、5 套 OAuth、5 套权限

**改用 Composio**：1 个 Key、1 套管理、500 个应用按需开。

---

## 六、对比

| 维度 | Composio | Zapier | Make | n8n |
|------|----------|--------|------|-----|
| **定位** | AI 集成 | 自动化 | 自动化 | 开源自动化 |
| **API 优先** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **应用数** | 500+ | 6000+ | 1500+ | 400+ |
| **Trigger** | ✅ | ✅ | ✅ | ✅ |
| **LLM 友好** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **自托管** | ❌ | ❌ | ❌ | ✅ |
| **价格** | 免费额度 + 付费 | 贵 | 中等 | 免费 |

> **AI 项目首选 Composio**（LLM 友好 + API 优先）；业务流程自动化选 Zapier / Make；数据敏感选 n8n 自托管。

---

## 七、注意事项

- **限流**：免费版 1000 action/月；高频用付费
- **OAuth 失效**：用户撤销授权时 Action 会失败；需要引导重新授权
- **Action 粒度**：每个应用的 Action 是预定义的；特殊需求用 custom action
- **Trigger 延迟**：webhook 通常 1~30 秒延迟
- **数据落地**：Composio 本身不存你的业务数据，只传 action 参数

---

## 八、相关工具

- [Slack](./Slack.md) - 单 Slack 用 Slack MCP 即可
- [Notion](./Notion.md) - 单 Notion 用 Notion MCP
- [Linear](./Linear.md) - 单 Linear 用 Linear MCP
- [GitHub](./GitHub.md) - 单 GitHub 用 GitHub MCP
- [钉钉](../../行业/即时通讯/钉钉.md) - 钉钉 Composio 支持有限
