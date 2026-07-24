# 🖥️ Desktop Commander MCP

> 分类：技术 / 后端（也常用于运维）
> 适用场景：终端命令执行、进程管理、文件编辑、本地开发操作

---

## 一、简介

Desktop Commander 把**本地 shell**暴露给 LLM。LLM 可以执行任意命令、查看进程、读 / 写文件、跑构建脚本、查日志、调试程序。
本质上是 SSH 到本机，但通过 MCP 包装后能被 LLM 安全调用。

> ⚠️ **能力非常强 = 风险也非常大**。生产环境必须做严格路径 + 命令白名单。

> 默认工具数：12

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 执行命令 | shell 命令、阻塞直到完成 |
| 后台进程 | 启动、查看、终止后台进程 |
| 文件操作 | 读、写、编辑（带 diff） |
| 目录操作 | 列表、创建、删除 |
| 路径搜索 | glob / regex 搜索文件内容 |
| 进程列表 | ps / 任务管理器 |
| 系统信息 | CPU / 内存 / 磁盘 / 网络 |
| 环境变量 | 查看 + 设置 |
| 包管理 | pip / npm / brew 包装/卸载 |
| Git 操作 | 简易 git 命令（推荐用专门的 Git MCP） |
| Docker 操作 | docker / docker compose 命令 |
| 定时任务 | crontab（Linux） |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
DESKTOP_BASE_PATH=/Users/yourname/projects  # 限制操作目录（必填）
DESKTOP_BLOCKED_PATHS=/etc,/usr,/var,/root,/System,/boot  # 禁止路径
DESKTOP_BLOCKED_COMMANDS=rm -rf /,dd,mkfs,fdisk,shutdown,reboot,halt,poweroff,init  # 禁止命令
```

### 可选

```bash
DESKTOP_DEFAULT_TIMEOUT=60  # 秒
DESKTOP_MAX_MEMORY=2048  # MB
DESKTOP_MAX_OUTPUT_SIZE=1048576  # 1MB
DESKTOP_ALLOW_BACKGROUND=true  # 是否允许后台进程
DESKTOP_AUDIT_LOG=./logs/desktop_commander.log  # 审计日志
DESKTOP_AUDIT_RETENTION_DAYS=90  # 日志保留天数
```

---

## 三、配置

### 3.1 路径白名单（必须）

```bash
# 必填：限制操作目录
DESKTOP_BASE_PATH=/Users/yourname/projects
# 所有读写必须在这个路径下（防止 rm -rf /）

# 必填：禁止的路径（前缀匹配）
DESKTOP_BLOCKED_PATHS=/etc,/usr,/var,/root,/System,/boot

# 必填：禁止的命令
DESKTOP_BLOCKED_COMMANDS=rm -rf /,dd,mkfs,fdisk,shutdown,reboot,halt,poweroff,init
```

### 3.2 超时 / 资源

```bash
# 命令默认超时（秒）
DESKTOP_DEFAULT_TIMEOUT=60

# 进程内存上限（MB）
DESKTOP_MAX_MEMORY=2048

# 单次输出大小（字节）
DESKTOP_MAX_OUTPUT_SIZE=1048576       # 1MB

# 是否允许后台进程
DESKTOP_ALLOW_BACKGROUND=true
```

### 3.3 日志

```bash
# 必填：审计日志路径
DESKTOP_AUDIT_LOG=./logs/desktop_commander.log

# 必填：日志保留天数
DESKTOP_AUDIT_RETENTION_DAYS=90
```

---

## 四、使用示例

### 4.1 执行命令

```bash
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/execute_command \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ls -la /Users/yourname/projects",
    "timeout_ms": 10000
  }'
```

### 4.2 读文件

```bash
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/read_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/main.py"
  }'
```

### 4.3 编辑文件（带 diff）

```bash
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/edit_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/main.py",
    "old_string": "def hello():\n    print(\"hello\")",
    "new_string": "def hello():\n    print(\"Hello, World!\")"
  }'
```

### 4.4 启动后台进程

```bash
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/start_process \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python -m http.server 8000",
    "working_dir": "/Users/yourname/projects/demo"
  }'
```

### 4.5 查看进程 / 终止

```bash
# 列出
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/list_processes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"filter": "python"}'

# 终止
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/kill_process \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"pid": 12345}'
```

### 4.6 搜索文件内容

```bash
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/search_content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src",
    "pattern": "TODO",
    "file_pattern": "*.py"
  }'
```

---

## 五、典型使用流程

### 场景：本地开发辅助 — LLM 帮你跑测试

```text
 用户            LLM            Desktop Commander        本地
  │               │                    │                │
  │ "跑测试"     │                    │                │
  ├──────────────▶│                    │                │
  │               │  execute_command   │                │
  │               │  pytest -v         │                │
  │               ├───────────────────▶│                │
  │               │                    │  路径检查 ✅   │
  │               │                    │  阻塞执行      │
  │               │                    ├───────────────▶│
  │               │                    │  exit_code: 0 │
  │               │                    │  23 passed    │
  │               │                    │◀───────────────┤
  │               │  结果分析          │                │
  │               │◀───────────────────┤                │
  │ "23 个测试通过"│                    │                │
  │◀──────────────┤                    │                │
```

### 场景：CI 调试 — 排查 runner 上失败原因

```text
 GitHub Actions  LLM         Desktop Commander     Runner 主机
     │             │               │                  │
     │  "CI 失败" │               │                  │
     ├────────────▶│               │                  │
     │             │  cat logs/test.log                │
     │             ├──────────────▶│                  │
     │             │               │  读文件         │
     │             │               ├─────────────────▶│
     │             │               │  tail 错误      │
     │             │               │◀─────────────────┤
     │             │  "缺少依赖"  │                  │
     │             │  pip install x │                 │
     │             ├──────────────▶│                  │
     │             │               │  安装包         │
     │             │               ├─────────────────▶│
     │             │               │  exit_code: 0   │
     │             │               │◀─────────────────┤
     │             │  重跑测试     │                  │
     │             ├──────────────▶│                  │
```

### 场景：批量处理脚本

```text
 LLM          Desktop Commander     目标目录
  │                │                  │
  │  find . -name "*.log" -mtime +30 │
  ├───────────────▶│                  │
  │                │  执行            │
  │                ├─────────────────▶│
  │                │  返回文件列表    │
  │                │◀─────────────────┤
  │                │                  │
  │  xargs rm     │                  │
  ├───────────────▶│                  │
  │                │  二次确认        │
  │                │  blocked_paths OK │
  │                │  删除 15 个文件  │
  │                ├─────────────────▶│
  │                │                  │
```

### 场景：危险命令拦截

```text
 LLM            Desktop Commander       系统
  │                 │                    │
  │  rm -rf /       │                    │
  ├────────────────▶│                    │
  │                 │  关键字匹配        │
  │                 │  ❌ "rm -rf /"     │
  │                 │  命中黑名单        │
  │                 │                    │
  │                 │  拒绝执行          │
  │                 ├───────────────────▶│
  │                 │  写审计日志        │
  │                 │  [WARN] blocked    │
  │                 │                    │
  │ "403 Forbidden: │
  │  blocked cmd"  │                    │
  │◀────────────────┤                    │
```

---

## 六、安全红线

> 🚨 **这是 MCP 里权限最大的一个，配置错误可能直接 rm -rf /**

必须做到：

1. **`DESKTOP_BASE_PATH` 必须设置**，且越窄越好
2. **`DESKTOP_BLOCKED_COMMANDS` 至少包含 `rm -rf /`、`dd`、`shutdown`**
3. **审计日志**全量记录，包括命令、参数、退出码
4. **生产环境**最好用 Docker / 沙箱跑 Desktop Commander，文件系统只读 mount
5. **API Key**鉴权，**不能只用 JWT**，因为一旦 Token 泄露 = 主机沦陷

参考：[OWASP LLM Top 10 - LLM07 System Prompt Leakage](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## 六、典型用法

- **本地开发** — LLM 帮你跑测试、装依赖、查日志
- **CI 调试** — 在 CI runner 上跑命令排查失败
- **运维巡检** — 定期跑 `df -h`、`ps aux`、`docker ps` 检查状态
- **批量脚本** — LLM 编排一连串命令

---

## 七、注意事项

- **绝对不要**在 MCP 服务器上跑公开访问，**仅限内网**
- **绝对不要**用 `root` / `Administrator` 启动 MCP 服务
- **路径越界保护**：即使设置了 `DESKTOP_BASE_PATH`，也要校验软链 / 绝对路径
- **Windows**：`cmd.exe` 和 `PowerShell` 行为不同，建议固定一种
- **临时文件**：执行命令时产生的临时文件要定期清理

---

## 八、相关工具

- [Filesystem](../运维/Filesystem.md) - 纯文件操作（无 shell）
- [Git](../运维/Git.md) - Git 命令更安全的封装
- [Docker](../运维/Docker.md)（可借 Desktop Commander 调） - 容器化部署

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Filesystem](技术/运维/Filesystem.md)

<!-- BACKLINKS END -->
