# 📋 Linear MCP

> 分类：技术 / 运维
> 官网：<https://linear.app/>
> 适用场景：敏捷开发、Issue 跟踪、Sprint 管理、Roadmap

---

## 一、简介

Linear 是工程师偏爱的项目管理工具，速度快、UI 简洁、键盘流友好。
MCP 集成后，LLM 可以：
- CRUD Issue
- 改状态、优先级、Assignee
- 管理 Project、Milestone
- 关联 PR
- 看 Cycle 数据

适用：Scrum / Kanban 团队、敏捷开发。

> 默认工具数：5

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| Issue CRUD | 创建、读、改、删除 |
| 状态 / 优先级 | 工作流流转 |
| Assignee / Label | 分配 + 标签 |
| Comment | 评论 |
| Project | 项目管理 |
| Cycle | Sprint |
| 关联 PR | 标记 PR 解决 Issue |
| 搜索 | 关键字 + 过滤 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxxxxx  # Personal API Key
```

### 可选

```bash
LINEAR_DEFAULT_TEAM=Engineering  # 默认团队
LINEAR_DEFAULT_ASSIGNEE=alice@company.com  # 默认 assignee
```

---

## 三、配置

### 3.1 申请 API Key

1. 打开 <https://linear.app/settings/api>
2. "Personal API keys" → "Create new"
3. 命名 → 选权限范围（建议只勾工作区必须的）
4. 复制 Key（`lin_api_` 开头）

### 3.2 环境变量

```bash
# 必填
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxxxxx

# 可选：默认团队
LINEAR_DEFAULT_TEAM=Engineering

# 可选：默认 assignee
# LINEAR_DEFAULT_ASSIGNEE=alice@company.com
```

---

## 四、使用示例

### 4.1 创建 Issue

```bash
curl -X POST http://localhost:8000/mcp/execute/linear/create_issue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "team": "Engineering",
    "title": "登录页报错 500",
    "description": "## 复现\n1. 打开 /login\n2. 提交表单\n3. 看到 500",
    "priority": 1,
    "labels": ["bug"],
    "assignee": "alice@company.com"
  }'
```

`priority`: 0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low

### 4.2 列 Issue

```bash
curl -X POST http://localhost:8000/mcp/execute/linear/list_issues \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "team": "Engineering",
    "state": ["In Progress", "Todo"],
    "assignee": "alice@company.com",
    "limit": 20
  }'
```

### 4.3 修改 Issue

```bash
curl -X POST http://localhost:8000/mcp/execute/linear/update_issue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": "ENG-123",
    "state": "Done",
    "assignee": "bob@company.com"
  }'
```

### 4.4 搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/linear/search_issues \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "login error",
    "limit": 10
  }'
```

### 4.5 添加评论

```bash
curl -X POST http://localhost:8000/mcp/execute/linear/add_comment \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": "ENG-123",
    "body": "已修复，PR #456"
  }'
```

---

## 五、典型使用流程

### 场景：Sentry 报错 → 自动建 Linear Issue

```text
 Sentry MCP        触发器            Linear MCP        Linear API
     │                │                  │                  │
     │  P0 新增      │                  │                  │
     ├───────────────▶│                  │                  │
     │                │  解析 + 格式化   │                  │
     │                │  - 标题          │                  │
     │                │  - 描述          │                  │
     │                │  - 优先级 P0     │                  │
     │                │  - 标签 bug      │                  │
     │                │                  │                  │
     │                │  create_issue   │                  │
     │                ├─────────────────▶│                  │
     │                │                  │  POST /issues    │
     │                │                  ├─────────────────▶│
     │                │                  │  ENG-456         │
     │                │                  │◀─────────────────┤
     │                │                  │                  │
     │                │  add_comment    │                  │
     │                │  (附 Sentry 链接)│                  │
     │                ├─────────────────▶│                  │
     │                │                  │                  │
     │                │                  │  自动 @ 相关人   │
     │                │                  │  + 邮件通知      │
     │                │                  │                  │
     │  工程师修复后   │                  │                  │
     │  git commit:   │                  │                  │
     │  "fix ENG-456" │                  │                  │
     │                │                  │                  │
     │                │  update_issue   │                  │
     │                │  state: Done    │                  │
     │                ├─────────────────▶│                  │
```

### 场景：Sprint 规划

```text
 产品经理         LLM              Linear MCP           Linear
     │               │                  │                  │
     │ "下个 Sprint  │                  │                  │
     │  规划"        │                  │                  │
     ├──────────────▶│                  │                  │
     │               │  1. 拉当前 Cycle │                  │
     │               │  2. 看 Backlog   │                  │
     │               │  3. 按容量评估   │                  │
     │               ├─────────────────▶│                  │
     │               │  [issue1: 5pt]  │                  │
     │               │  [issue2: 3pt]  │                  │
     │               │  [issue3: 8pt]  │                  │
     │               │◀─────────────────┤                  │
     │               │                  │                  │
     │               │  批量 update_issue (cycle: Sprint 24)│
     │               │  + assignee     │                  │
     │               ├─────────────────▶│                  │
     │               │                  │  12 issues moved │
     │               │                  │  to current cycle│
     │               │                  │                  │
     │ "Sprint 24 已规划"                              │
     │◀──────────────┤                  │                  │
```

### 场景：状态变更通知

```text
 Linear            触发器             Slack MCP         Slack
   │                 │                    │                │
   │  status: Done  │                    │                │
   ├────────────────▶│                    │                │
   │                 │  查 issue 信息     │                │
   │                 │  - 标题           │                │
   │                 │  - 负责人         │                │
   │                 │                    │                │
   │                 │  send_blocks       │                │
   │                 ├───────────────────▶│                │
   │                 │                    │  #dev-alerts   │
   │                 │                    │  ┌─────────┐  │
   │                 │                    │  │ ✅ 完成  │  │
   │                 │                    │  │ ENG-456 │  │
   │                 │                    │  │ 修复登录│  │
   │                 │                    │  │ @bob    │  │
   │                 │                    │  └─────────┘  │
```

---

## 六、对比 GitHub Issues / Jira

| 维度 | Linear | GitHub Issues | Jira |
|------|--------|---------------|------|
| **速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **UX** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **企业特性** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **API 易用** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **价格** | 免费版够用 | 免费 | 贵 |
| **适合** | 创业 / 中小团队 | 开源 / 强 GitHub 集成 | 大企业 / 复杂流程 |

> **小到中型团队首选 Linear**；重度 GitHub 集成选 GitHub Issues；大企业 / 复杂流程选 Jira。

---

## 七、注意事项

- **API 限流**：1500 req/h，复杂查询 1.5 req/s
- **Webhooks**：实时性要求高的场景用 Webhook
- **Issue ID**：形式 `TEAM-NUMBER`（如 `ENG-123`）
- **Cycle**：Sprint 概念，每 1~4 周一个
- **Roadmap**：时间线视图，适合做版本规划

---

## 八、相关工具

- [GitHub](./GitHub.md) - commit / PR 关联
- [Sentry](../测试/Sentry.md) - 错误自动建单
- [Notion](./Notion.md) - 文档 / 知识库
- [Slack](./Slack.md) - 状态变更通知

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Sentry](技术/测试/Sentry.md)
- [Memory](技术/知识库/Memory.md)
- [Composio](技术/运维/Composio.md)
- [GitHub](技术/运维/GitHub.md)
- [Google-Sheets](技术/运维/Google-Sheets.md)
- [Notion](技术/运维/Notion.md)
- [Slack](技术/运维/Slack.md)

<!-- BACKLINKS END -->
