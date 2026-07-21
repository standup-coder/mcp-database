# 💬 Slack MCP

> 分类：技术 / 运维
> 适用场景：消息推送、频道管理、机器人、告警通知、互动卡片

---

## 一、简介

Slack MCP 把 Slack API 暴露给 LLM。LLM 可以：
- 推送消息到频道 / 私聊
- 用 Block Kit 构造富文本卡片
- 管理频道、成员
- 读消息历史
- 互动（按钮 / 下拉）

适用：CI 通知、监控告警、值班提醒、团队协作机器人。

> 默认工具数：8

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 发消息 | 文本 / Block Kit / 附件 |
| 读历史 | 频道 / 私聊 |
| 上传文件 | 图片 / 文档 |
| 频道管理 | 创建 / 邀请 / 归档 |
| 互动响应 | 按钮 / Modal 提交 |
| 用户查询 | 邮箱 → 用户 ID |
| 状态 | 设置机器人状态 |
| 搜索 | 关键字搜索消息 |

---

## 三、配置

### 3.1 创建 Slack App

1. 打开 <https://api.slack.com/apps>
2. "Create New App" → "From scratch"
3. 命名 + 选 workspace
4. 左侧 "OAuth & Permissions" → 添加 Bot Token Scopes：
   - `chat:write`
   - `chat:write.public`
   - `channels:read`
   - `channels:history`
   - `users:read`
   - `files:write`
5. 装到 workspace → 复制 **Bot User OAuth Token**（`xoxb-` 开头）
6. **Signing Secret** 在 "Basic Information" 页面

### 3.2 环境变量

```bash
# 必填
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxxxxxx

# 可填（事件订阅需要）
SLACK_SIGNING_SECRET=your_signing_secret

# 可选：默认频道
SLACK_DEFAULT_CHANNEL=#general

# 可选：API base（自托管）
# SLACK_API_BASE=https://slack.example.com/api
```

---

## 四、使用示例

### 4.1 发送文本消息

```bash
curl -X POST http://localhost:8000/mcp/execute/slack/send_message \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#dev-alerts",
    "text": "CI 失败：PR #123\n查看: https://github.com/..."
  }'
```

### 4.2 发送 Block Kit 卡片

```bash
curl -X POST http://localhost:8000/mcp/execute/slack/send_blocks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#dev-alerts",
    "blocks": [
      {
        "type": "header",
        "text": {"type": "plain_text", "text": "🚨 生产告警"}
      },
      {
        "type": "section",
        "fields": [
          {"type": "mrkdwn", "text": "*服务*\norder-service"},
          {"type": "mrkdwn", "text": "*错误率*\n5.2%"}
        ]
      },
      {
        "type": "actions",
        "elements": [
          {
            "type": "button",
            "text": {"type": "plain_text", "text": "查看 Dashboard"},
            "url": "https://grafana.example.com/d/123"
          }
        ]
      }
    ]
  }'
```

### 4.3 上传文件

```bash
curl -X POST http://localhost:8000/mcp/execute/slack/upload_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#dev-alerts",
    "file_path": "./logs/error.log",
    "filename": "error.log",
    "title": "Error log"
  }'
```

### 4.4 读历史

```bash
curl -X POST http://localhost:8000/mcp/execute/slack/list_messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#dev-alerts",
    "limit": 20,
    "oldest": "2024-09-15T00:00:00Z"
  }'
```

### 4.5 搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/slack/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deploy failed",
    "count": 10
  }'
```

### 4.6 用户查询

```bash
curl -X POST http://localhost:8000/mcp/execute/slack/get_user \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@company.com"
  }'
```

---

## 五、典型使用流程

### 场景：CI 失败告警 + 一键操作

```text
 GitHub Actions       GitHub MCP          LLM         Slack MCP           Slack
     │                    │                │              │                │
 CI ❌│                    │                │              │                │
     │   list_workflow_runs                │              │                │
     ├───────────────────▶│                │              │                │
     │   run #567 failed  │                │              │                │
     │                    │  拉日志       │              │                │
     │                    ├───────────────▶│              │                │
     │                    │                │  摘要失败原因                │
     │                    │                │              │                │
     │                    │                │  send_blocks                 │
     │                    │                │  header + actions            │
     │                    │                ├─────────────▶│                │
     │                    │                │              │  POST chat    │
     │                    │                │              │  .postMessage  │
     │                    │                │              ├───────────────▶│
     │                    │                │              │                │
     │                    │                │              │  #dev-alerts  │
     │                    │                │              │  ┌─────────┐ │
     │                    │                │              │  │ 🚨 CI 失败│ │
     │                    │                │              │  │ [日志]   │ │
     │                    │                │              │  │ [重跑]   │ │
     │                    │                │              │  │ [详情]   │ │
     │                    │                │              │  └─────────┘ │
     │                    │                │              │                │
     │   工程师点"重跑"  │                │              │                │
     │◀───────────────────┼────────────────┼──────────────┤                │
     │                    │                │              │  Interaction  │
     │   re-run           │                │              │  → dispatch   │
     ├────────────────────▶                │              │                │
     │                    │                │              │                │
```

### 场景：每日站会机器人

```text
 定时任务            Slack MCP              Slack
  09:00 周一            │                   │
     │  send_blocks    │                   │
     │  daily standup  │                   │
     ├─────────────────▶│                   │
     │                 │  拉本周统计       │
     │                 │  (PR数, Issue数)  │
     │                 │                   │
     │                 │  发送卡片         │
     │                 ├──────────────────▶│
     │                 │                   │
     │                 │  #standup 频道    │
     │                 │  ┌────────────┐   │
     │                 │  │ 周一站会   │   │
     │                 │  │ 📊 本周:   │   │
     │                 │  │ - 12 PR    │   │
     │                 │  │ - 5 Issue  │   │
     │                 │  │ [看详情]   │   │
     │                 │  └────────────┘   │
```

### 场景：交互式 Modal 表单

```text
 用户             Slack MCP             Slack
  │                 │                    │
  │  点"创建工单" │                    │
  ├────────────────▶│                    │
  │                 │  views.open         │
  │                 │  (Modal 表单)      │
  │                 ├───────────────────▶│
  │                 │                    │
  │  弹窗输入        │                    │
  │  - 标题        │                    │
  │  - 描述        │                    │
  │  - 优先级      │                    │
  │                 │                    │
  │  点提交         │                    │
  ├────────────────▶│                    │
  │                 │  view_submission   │
  │                 │  (callback)        │
  │                 │                    │
  │  创建 Linear Issue
```

---

## 六、Block Kit 速查

Block Kit 是 Slack 的富文本格式，常见块：

| Block | 用途 |
|-------|------|
| `header` | 大标题 |
| `section` | 段落 + 字段 |
| `divider` | 分隔线 |
| `actions` | 按钮 / 下拉 |
| `context` | 小字补充信息 |
| `image` | 图片 |
| `input` | Modal 输入 |

设计器：<https://app.slack.com/block-kit-builder>

---

## 七、对比钉钉

| 维度 | Slack | 钉钉 |
|------|-------|------|
| **国际化** | 海外首选 | 国内首选 |
| **API 友好** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Block Kit** | ⭐⭐⭐⭐⭐ | ActionCard |
| **价格** | 免费版限 10k 条消息 | 免费 |
| **集成** | 2400+ App | 较 Slack 少 |

> 国内团队用钉钉，海外用 Slack；同公司两个都支持也不冲突。

---

## 八、注意事项

- **OAuth Scope**：只给必要的 scope，避免 Token 滥用
- **限流**：每秒 1 条消息（不同方法不同）
- **私聊**：发私聊前必须有 user ID（通过 `users.lookupByEmail` 拿）
- **Block Kit 大小**：单消息 50 个 block 限制
- **归档频道**：只读，不能发

---

## 九、相关工具

- [GitHub](./GitHub.md) - PR 通知
- [Sentry](../测试/Sentry.md) - 错误告警
- [Linear](./Linear.md) - Issue 状态变更通知
- [钉钉](../../行业/即时通讯/钉钉.md) - 国内场景替代
