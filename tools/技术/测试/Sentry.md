# 🐛 Sentry MCP（错误监控）

> 分类：技术 / 测试（也常用于运维）
> 官网：<https://sentry.io/>
> 适用场景：错误监控、Issue 跟踪、事件分析、故障排查

---

## 一、简介

Sentry 是业界最流行的应用错误监控平台。MCP 集成后，LLM 可以：
- 列出未解决的 Issue
- 查看具体错误堆栈
- 拉取事件详情
- 标记 / 解决 / 分配 Issue
- 看性能数据

适用：生产故障排查、错误模式分析、值班响应。

> 默认工具数：8

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 列 Issue | 按项目 / 状态 / 时间 |
| Issue 详情 | 错误堆栈、上下文、设备 |
| 事件列表 | 该 Issue 下的所有事件 |
| 解决 / 分配 | 更新 Issue 状态 |
| 性能 | 慢事务、APM 数据 |
| Release 跟踪 | 看 Release 引入了哪些错误 |
| Source Map | 反混淆 JS 错误 |
| 告警规则 | 查看 / 创建告警 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
SENTRY_ACCESS_TOKEN=sntrys_xxxxxxxxxxxxxxxx  # Auth Token
```

### 可选

```bash
SENTRY_HOST=sentry.io  # 自托管时改
SENTRY_DEFAULT_PROJECT=my-app  # 默认项目
SENTRY_SELF_HOSTED=false  # true/false
SENTRY_SCHEME=https  # https/http
```

---

## 三、配置

### 3.1 申请 Auth Token

1. 登录 Sentry → Settings → Account → API → Auth Tokens
2. Create New Token
3. 勾选需要的 scope（`event:read`、`event:write`、`project:read`、`project:write`、`org:read`）
4. 复制 Token

### 3.2 环境变量

```bash
# 必填
SENTRY_ACCESS_TOKEN=sntrys_xxxxxxxxxxxxxxxx

# 可选：Sentry Host（自托管时改）
# SENTRY_HOST=sentry.example.com

# 可选：组织 slug
# SENTRY_ORG=my-org

# 默认项目
SENTRY_DEFAULT_PROJECT=my-app

# 是否自托管
SENTRY_SELF_HOSTED=false
```

### 3.3 自托管 Sentry

```bash
SENTRY_HOST=sentry.internal.company.com
SENTRY_SELF_HOSTED=true
SENTRY_SCHEME=https
```

---

## 四、使用示例

### 4.1 列出未解决 Issue

```bash
curl -X POST http://localhost:8000/mcp/execute/sentry/list_issues \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "my-app",
    "status": "unresolved",
    "limit": 20
  }'
```

返回（简化）：

```json
{
  "issues": [
    {
      "id": "123456",
      "title": "TypeError: Cannot read property 'id' of undefined",
      "count": 142,
      "userCount": 87,
      "lastSeen": "2024-09-15T08:30:00Z",
      "level": "error",
      "culprit": "app.services.order.getOrder"
    }
  ]
}
```

### 4.2 查看 Issue 详情

```bash
curl -X POST http://localhost:8000/mcp/execute/sentry/get_issue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id_or_url": "https://sentry.io/organizations/my-org/issues/123456/"
  }'
```

返回：

```json
{
  "id": "123456",
  "title": "TypeError: Cannot read property 'id' of undefined",
  "stacktrace": [
    {
      "function": "getOrder",
      "filename": "app/services/order.js",
      "lineno": 42,
      "context": "  return order.user.id;"
    }
  ],
  "tags": {
    "environment": "production",
    "release": "v1.2.3",
    "browser": "Chrome 128"
  }
}
```

### 4.3 列出事件

```bash
curl -X POST http://localhost:8000/mcp/execute/sentry/list_events \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": "123456",
    "limit": 10
  }'
```

### 4.4 解决 / 分配

```bash
# 解决
curl -X POST http://localhost:8000/mcp/execute/sentry/resolve_issue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": "123456",
    "status": "resolved"
  }'

# 分配
curl -X POST http://localhost:8000/mcp/execute/sentry/assign_issue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": "123456",
    "assignee": "alice@company.com"
  }'
```

### 4.5 性能数据

```bash
curl -X POST http://localhost:8000/mcp/execute/sentry/transaction_stats \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "my-app",
    "transaction": "/api/orders",
    "statsPeriod": "24h"
  }'
```

---

## 五、典型使用流程

### 场景：Sentry 报错 → 自动排查 → 提 PR

```text
  Sentry       告警触发        Sentry MCP         LLM           GitHub MCP         Linear MCP         钉钉 MCP
    │             │               │                │                │                 │                  │
    │  P0 新增   │               │                │                │                 │                  │
    ├────────────▶│               │                │                │                 │                  │
    │             │  Webhook     │                │                │                 │                  │
    │             ├─────────────▶│                │                │                 │                  │
    │             │               │  get_issue    │                │                 │                  │
    │             │               ├───────────────▶│                │                 │                  │
    │             │               │               │  list_recent   │                 │                  │
    │             │               │               │  commits       │                 │                  │
    │             │               │               ├───────────────▶│                 │                  │
    │             │               │               │               │                 │                  │
    │             │               │               │  "v1.2.3 commit abc 引入"          │                  │
    │             │               │               │◀──────────────┤                 │                  │
    │             │               │               │                                  │                  │
    │             │               │               │  Sequential Thinking 推理         │                  │
    │             │               │               │  根因: 未处理空值                │                  │
    │             │               │               │                                  │                  │
    │             │               │               │  create_issue                                    │
    │             │               │               ├──────────────────────────────────▶│                  │
    │             │               │               │               │                 │  ENG-456          │
    │             │               │               │               │                 │                  │
    │             │               │               │  add_comment (根因分析)          │                  │
    │             │               │               ├──────────────────────────────────▶│                  │
    │             │               │               │               │                 │                  │
    │             │               │               │  send_text 通知值班人            │                  │
    │             │               │               ├───────────────────────────────────────────────────▶│
    │             │               │               │               │                 │      @值班人
```

### 场景：周期性健康巡检

```text
  Celery Beat        Sentry MCP          LLM          钉钉 MCP
   每天 09:00             │                │                │
      │   list_issues    │                │                │
      │  status:unresolved                │                │
      ├─────────────────▶│                │                │
      │                  │  12 个 unresolved                │
      │◀─────────────────┤                │                │
      │                  │                │                │
      │                  │  分级统计       │                │
      │                  │  P0: 1         │                │
      │                  │  P1: 3         │                │
      │                  │  P2: 8         │                │
      │                  │                │                │
      │                  │  摘要 + 建议   │                │
      │                  │◀───────────────┤                │
      │                  │                │                │
      │                  │   send_markdown│                │
      ├──────────────────┼────────────────▶│                │
      │                  │                │  每日健康报告  │
      │                  │                ├───────────────▶│
```

### 场景：分析错误模式

```text
 LLM              Sentry MCP                模式分析
  │                   │                       │
  │  list_issues      │                       │
  │  last 7 days      │                       │
  ├──────────────────▶│                       │
  │                   │  50 个错误            │
  │                   │◀──────────────────────┤
  │                   │                       │
  │  group_by         │                       │
  │  - file           │                       │
  │  - error type     │                       │
  ├──────────────────▶│                       │
  │                   │  6 类错误             │
  │                   │  Top 1: null ref     │
  │                   │  Top 2: timeout      │
  │                   │◀──────────────────────┤
  │                   │                       │
  │  "主要问题:       │                       │
  │   1. order_svc 缺空值校验            │
  │   2. payment_svc 超时"               │
  │                   │                       │
  │  提 2 个 PR       │                       │
```

---

## 六、对比其他错误监控

| 平台 | 特点 |
|------|------|
| **Sentry** | 主流、多语言、Source Map、Release 跟踪 |
| **Bugsnag** | 简洁、移动端友好 |
| **Rollbar** | 老牌、自动化分组 |
| **DataDog APM** | 一体化（监控 + 日志 + 错误） |
| **GlitchTip** | Sentry 兼容的开源替代 |

---

## 七、注意事项

- **Token 权限**：只勾必要的 scope，别给 `org:admin`
- **大量 Issue**：用 `query` 过滤（如 `firstSeen:>2024-09-01`）
- **隐私**：Sentry 会收集用户 IP / 设备，注意合规
- **性能开销**：每个错误都上报可能影响性能；阈值要合理
- **保留期**：默认 90 天，超期事件可能查不到

---

## 八、相关工具

- [GitHub](../运维/GitHub.md) - 查相关 commit / PR
- [Linear](../运维/Linear.md) - 自动建工单跟踪
- [钉钉](../../行业/即时通讯/钉钉.md) - 实时推送新 Issue
- [Sequential Thinking](../知识库/Sequential-Thinking.md) - 故障排查推理

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Browser](技术/前端/Browser.md)
- [Database](技术/后端/Database.md)
- [Git](技术/运维/Git.md)
- [GitHub](技术/运维/GitHub.md)
- [Linear](技术/运维/Linear.md)
- [Slack](技术/运维/Slack.md)

<!-- BACKLINKS END -->
