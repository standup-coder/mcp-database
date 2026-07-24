# 🔧 Git MCP

> 分类：技术 / 运维
> 适用场景：版本控制、commit、branch、diff、log、merge、rebase

---

## 一、简介

Git MCP 把 Git 命令包装成 LLM 可调用的工具。LLM 可以：
- 查 log / diff / status
- 创建 / 切换 / 删除分支
- 提交 / 推送 / 拉取
- 合并 / 变基 / 解决冲突
- 标签管理

比 Desktop Commander 调 `git` 命令更安全：参数校验、禁止危险操作。

> 默认工具数：9

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 状态 | `git status` |
| 日志 | `git log`，支持过滤 |
| 差异 | `git diff`，文件级 / 行级 |
| 提交 | add + commit（可分阶段） |
| 分支 | 创建 / 切换 / 删除 / 列出 |
| 远程 | push / pull / fetch |
| 合并 | merge / rebase |
| 标签 | 创建 / 列出 / 推送 |
| 储藏 | stash |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
GIT_BASE_PATH=/Users/yourname/projects  # 仓库根目录
GIT_ALLOWED_REMOTES=origin,upstream  # 允许的远程
GIT_PROTECTED_BRANCHES=main,master,develop  # 保护分支
```

### 强烈建议（生产环境）

```bash
GIT_ALLOW_FORCE_PUSH=false  # 禁止 force push
GIT_ALLOW_HARD_RESET=false  # 禁止 hard reset
```

### 可选

```bash
GIT_USER_NAME=MCP Bot  # 提交用户名
GIT_USER_EMAIL=mcp@company.com  # 提交邮箱
```

---

## 三、配置

### 3.1 路径白名单

```bash
# 必填：仓库根目录
GIT_BASE_PATH=/Users/yourname/projects

# 必填：允许操作的远程
GIT_ALLOWED_REMOTES=origin,upstream
```

### 3.2 用户信息

```bash
# 可选：全局 Git 用户（用于 commit）
GIT_USER_NAME="MCP Bot"
GIT_USER_EMAIL="mcp@company.com"

# 可选：默认编辑器
GIT_EDITOR=vim

# 可选：签名 key
# GIT_SIGNING_KEY=~/.ssh/git_signing_key
```

### 3.3 危险操作

```bash
# 禁止 force push（推荐）
GIT_ALLOW_FORCE_PUSH=false

# 禁止 hard reset
GIT_ALLOW_HARD_RESET=false

# 禁止删除主分支
GIT_PROTECTED_BRANCHES=main,master,develop
```

---

## 四、使用示例

### 4.1 看状态

```bash
curl -X POST http://localhost:8000/mcp/execute/git/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"path": "my-repo"}'
```

### 4.2 看提交日志

```bash
curl -X POST http://localhost:8000/mcp/execute/git/log \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-repo",
    "max_count": 10,
    "branch": "main"
  }'
```

### 4.3 看 diff

```bash
curl -X POST http://localhost:8000/mcp/execute/git/diff \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-repo",
    "ref1": "HEAD~1",
    "ref2": "HEAD"
  }'
```

### 4.4 提交

```bash
# 阶段 + 提交
curl -X POST http://localhost:8000/mcp/execute/git/commit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-repo",
    "message": "feat: add user login\n\n- Add Login component\n- Add auth context",
    "add_all": true
  }'
```

### 4.5 分支操作

```bash
# 创建并切换
curl -X POST http://localhost:8000/mcp/execute/git/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-repo",
    "branch": "feature/new-dashboard",
    "create": true
  }'

# 列出所有分支
curl -X POST http://localhost:8000/mcp/execute/git/list_branches \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-repo",
    "include_remote": true
  }'
```

### 4.6 推送

```bash
curl -X POST http://localhost:8000/mcp/execute/git/push \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-repo",
    "remote": "origin",
    "branch": "feature/new-dashboard",
    "set_upstream": true
  }'
```

---

## 五、典型使用流程

### 场景：完整 PR 工作流

```text
  LLM            Git MCP          本地仓库          GitHub MCP
   │                │                │                  │
   │  checkout      │                │                  │
   │  -b feature/x                  │                  │
   │  from main    │                │                  │
   ├───────────────▶│                │                  │
   │                │  git switch    │                  │
   │                ├───────────────▶│                  │
   │                │◀───────────────┤                  │
   │                │                │                  │
   │  Filesystem 改文件                                │
   │  edit_file ...                                    │
   │                │                │                  │
   │  status       │                │                  │
   ├───────────────▶│                │                  │
   │                │  3 modified   │                  │
   │◀───────────────┤                │                  │
   │                │                │                  │
   │  commit       │                │                  │
   │  message + add_all               │                  │
   ├───────────────▶│                │                  │
   │                │  git commit   │                  │
   │                ├───────────────▶│                  │
   │                │  abc1234      │                  │
   │                │◀───────────────┤                  │
   │                │                │                  │
   │  push         │                │                  │
   │  -u origin feature/x            │                  │
   ├───────────────▶│                │                  │
   │                │  git push    │                  │
   │                ├───────────────▶│                  │
   │                │               ─┼───────────────▶│
   │                │                │  push success   │
   │                │                │                  │
   │  create_pull_request                                │
   ├───────────────────────────────────────────────────▶│
   │                │                │                  │
   │                │                │   PR #456 open
```

### 场景：主分支保护

```text
 LLM            Git MCP           审计
  │                │                │
  │  push origin main                │
  ├───────────────▶│                │
  │                │  检查保护分支  │
  │                │  ❌ main 在   │
  │                │  protected     │
  │                │                │
  │                │  拒绝 + 日志   │
  │                ├───────────────▶│
  │                │                │
  │ "403 Forbidden:│                │
  │  main protected"                 │
  │◀───────────────┤                │
```

### 场景：force push 拦截

```text
 LLM            Git MCP           审计
  │                │                │
  │  push --force origin main        │
  ├───────────────▶│                │
  │                │  检查允许标志  │
  │                │  ❌ force push │
  │                │  禁用         │
  │                │                │
  │ "403 Forbidden:│                │
  │  force push    │                │
  │  not allowed"  │                │
  │◀───────────────┤                │
```

---

## 六、安全注意事项

1. **`GIT_ALLOW_FORCE_PUSH=false`**：默认禁止 force push
2. **`GIT_PROTECTED_BRANCHES`**：主分支不允许直接 commit / push
3. **审计日志**：所有 git 操作记录（who / what / when）
4. **签名**：GPG / SSH 签名 commit，可选开启
5. **凭证**：用 SSH key 而非密码；key 放在 `GIT_BASE_PATH` 外

---

## 七、相关工具

- [GitHub](./GitHub.md) - 上游：PR / Issue / Review
- [Filesystem](./Filesystem.md) - 改文件
- [Sentry](../测试/Sentry.md) - commit 信息可以关联 Sentry Issue

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Desktop-Commander](技术/后端/Desktop-Commander.md)
- [Filesystem](技术/运维/Filesystem.md)
- [GitHub](技术/运维/GitHub.md)

<!-- BACKLINKS END -->
