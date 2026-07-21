# 📦 GitHub MCP

> 分类：技术 / 运维
> 官网：<https://github.com/>
> 适用场景：仓库管理、Issue、PR、Code Search、Release、Actions

---

## 一、简介

GitHub MCP 把 GitHub API 暴露给 LLM。LLM 可以：
- 读 Issue / PR / Discussion
- 写评论、改状态、合并 PR
- 搜索代码 / 仓库
- 管理 Release / Tag
- 看 Actions 运行状态

> 默认工具数：10

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 仓库 | 列表 / 详情 / 创建 |
| Issue | CRUD、评论、标签 |
| PR | CRUD、Review、合并 |
| 代码搜索 | 跨仓库关键字 |
| Release | 创建 / 列表 / 下载 |
| Actions | 触发 / 查运行状态 |
| Discussion | 读 / 写 |
| 文件 | 读仓库内文件 |

---

## 三、配置

### 3.1 申请 Token

1. 打开 <https://github.com/settings/tokens>
2. **Classic Token** 或 **Fine-grained Token**（推荐后者，权限更细）
3. 勾选必要的 scope：
   - `repo`（仓库读写）
   - `read:user`
   - `workflow`（Actions）
4. 复制 Token

### 3.2 环境变量

```bash
# 必填
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx

# 可选：GitHub Enterprise
# GITHUB_HOST=https://github.example.com

# 可选：API base
GITHUB_API_BASE=https://api.github.com

# 可选：默认用户 / 组织
# GITHUB_DEFAULT_OWNER=my-org
```

---

## 四、使用示例

### 4.1 列仓库

```bash
curl -X POST http://localhost:8000/mcp/execute/github/list_repos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "type": "all"
  }'
```

### 4.2 搜索代码

```bash
curl -X POST http://localhost:8000/mcp/execute/github/search_code \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "function main language:python repo:my-org/my-repo"
  }'
```

### 4.3 列 Issue

```bash
curl -X POST http://localhost:8000/mcp/execute/github/list_issues \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "repo": "my-repo",
    "state": "open",
    "labels": ["bug"]
  }'
```

### 4.4 创建 Issue

```bash
curl -X POST http://localhost:8000/mcp/execute/github/create_issue \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "repo": "my-repo",
    "title": "登录页报错",
    "body": "## 复现\n1. 打开 /login\n2. 提交表单\n3. 看到 500",
    "labels": ["bug", "P0"]
  }'
```

### 4.5 创建 PR

```bash
curl -X POST http://localhost:8000/mcp/execute/github/create_pull_request \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "repo": "my-repo",
    "title": "fix: handle 500 on login",
    "head": "feature/fix-login",
    "base": "main",
    "body": "## 改动\n修复登录时的 500 错误\n\nCloses #123",
    "draft": true
  }'
```

### 4.6 合并 PR

```bash
curl -X POST http://localhost:8000/mcp/execute/github/merge_pull_request \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "repo": "my-repo",
    "pull_number": 456,
    "merge_method": "squash"
  }'
```

### 4.7 触发 Actions

```bash
curl -X POST http://localhost:8000/mcp/execute/github/dispatch_workflow \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "repo": "my-repo",
    "workflow_id": "deploy.yml",
    "ref": "main",
    "inputs": {"environment": "staging"}
  }'
```

### 4.8 Release

```bash
# 创建
curl -X POST http://localhost:8000/mcp/execute/github/create_release \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "my-org",
    "repo": "my-repo",
    "tag_name": "v1.2.3",
    "name": "v1.2.3 - Bug Fixes",
    "body": "## Changes\n- Fix login error",
    "draft": false,
    "prerelease": false
  }'
```

---

## 五、典型使用流程

### 场景：Sentry 报错 → 自动排查 → 提 PR（端到端）

```text
 Sentry MCP    Sequential     Filesystem    Git MCP      GitHub MCP     钉钉 MCP
     │           Thinking          │            │              │             │
     │  拉错误   │                │            │              │             │
     ├──────────▶│                │            │              │             │
     │           │  多步推理     │            │              │             │
     │           │  根因: 空指针  │            │              │             │
     │           │                │            │              │             │
     │           │  改代码       │            │              │             │
     │           ├───────────────▶│            │              │             │
     │           │                │  edit_file │              │             │
     │           │                │  校验路径  │              │             │
     │           │                │  写新代码  │              │             │
     │           │                │            │              │             │
     │           │  commit       │            │              │             │
     │           ├────────────────────────────▶│              │             │
     │           │                │            │  commit +    │             │
     │           │                │            │  push        │             │
     │           │                │            ├─────────────▶│             │
     │           │                │            │              │  push 成功  │
     │           │                │            │              │             │
     │           │  create_pull_request        │              │             │
     │           ├─────────────────────────────────────────▶│             │
     │           │                │            │              │             │
     │           │                │            │              │  PR #456   │
     │           │                │            │              │             │
     │           │  send_text (通知开发者)                    │             │
     │           ├────────────────────────────────────────────────────────▶│
     │           │                │            │              │   @开发者
```

### 场景：批量管理 Issue

```text
 LLM           GitHub MCP                GitHub API
  │                │                         │
  │  list_issues   │                         │
  │  labels=bug    │                         │
  ├───────────────▶│                         │
  │                │  GET /repos/.../issues  │
  │                ├────────────────────────▶│
  │                │◀────────────────────────┤
  │  30 个        │                         │
  │◀───────────────┤                         │
  │                │                         │
  │  按规则分类    │                         │
  │  - 错误率高 → P0                          │
  │  - 重复 → close as dup                    │
  │                │                         │
  │  update_issue (批量)                      │
  ├───────────────▶│                         │
  │                │  PATCH × 30             │
  │                ├────────────────────────▶│
  │                │                         │
  │  30/30 完成   │                         │
  │◀───────────────┤                         │
```

### 场景：自动 Release

```text
 触发器            GitHub MCP              GitHub Actions
 main 分支合并           │                        │
     │   get latest tag   │                        │
     ├───────────────────▶│                        │
     │                    │  GET tags              │
     │                    │                        │
     │   bump version     │                        │
     │   v1.2.3 → v1.2.4  │                        │
     │                    │                        │
     │   create_release   │                        │
     ├───────────────────▶│                        │
     │                    │  POST /releases        │
     │                    │                        │
     │   dispatch_workflow (build docker)            │
     ├───────────────────▶│                        │
     │                    │  trigger build.yml     │
     │                    ├───────────────────────▶│
     │                    │                        │
     │   "发布 v1.2.4"   │                        │
```

---

## 六、注意事项

- **Token 权限**：Fine-grained Token 优先；只给必要仓库
- **Rate Limit**：未认证 60/h，认证 5000/h；超出 429
- **Webhook**：高频写操作建议配合 Webhook
- **PR Review**：建议仍由人 review，LLM 不应自动合主干
- **签名 commit**：保护 main 分支必须签名

---

## 七、相关工具

- [Git](./Git.md) - 本地仓库操作
- [Linear](./Linear.md) - Issue / Project 同步
- [Sentry](../测试/Sentry.md) - commit 信息关联 Sentry Issue
