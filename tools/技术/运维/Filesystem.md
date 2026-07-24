# 📁 Filesystem MCP

> 分类：技术 / 运维
> 适用场景：本地文件读写、目录操作、文件搜索、批量重命名

---

## 一、简介

Filesystem MCP 给 LLM 提供了**受限的文件系统访问能力**。与 Desktop Commander 的区别：
- **Filesystem**：纯文件操作（读 / 写 / 列表 / 搜索），无 shell
- **Desktop Commander**：可以执行任意命令

Filesystem 更安全（没有 shell 注入风险），适合纯文件场景。

> 默认工具数：7

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 读文件 | 文本 / 二进制 |
| 写文件 | 创建 / 覆盖 / 追加 |
| 编辑文件 | 字符串替换（带 diff 预览） |
| 列表 | 目录内容（含隐藏文件） |
| 创建 / 删除 | 目录 + 文件 |
| 移动 / 重命名 | 文件 / 目录 |
| 搜索 | glob 模式 + 内容搜索 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
FILESYSTEM_BASE_PATH=/Users/yourname/projects  # 根目录
FILESYSTEM_BLOCKED_PATHS=/etc,/usr,/var,/root,/System,/boot,.ssh,.aws  # 禁止路径
FILESYSTEM_BLOCKED_EXTENSIONS=.env,.key,.pem,.pfx,.p12,.cer  # 禁止后缀
```

### 可选

```bash
FILESYSTEM_MAX_FILE_SIZE=10485760  # 10MB
FILESYSTEM_MAX_LIST_DEPTH=10
FILESYSTEM_MAX_SEARCH_RESULTS=1000
```

---

## 三、配置

### 3.1 路径白名单（必须）

```bash
# 必填：根目录，所有操作在此之下
FILESYSTEM_BASE_PATH=/Users/yourname/projects

# 必填：禁止路径（前缀匹配）
FILESYSTEM_BLOCKED_PATHS=/etc,/usr,/var,/root,/System,/boot,.ssh,.aws

# 必填：禁止的文件后缀
FILESYSTEM_BLOCKED_EXTENSIONS=.env,.key,.pem,.pfx,.p12,.cer
```

### 3.2 资源限制

```bash
# 单文件最大大小（字节）
FILESYSTEM_MAX_FILE_SIZE=10485760     # 10MB

# 列表深度
FILESYSTEM_MAX_LIST_DEPTH=10

# 搜索结果数
FILESYSTEM_MAX_SEARCH_RESULTS=1000
```

---

## 四、使用示例

### 4.1 读文件

```bash
curl -X POST http://localhost:8000/mcp/execute/filesystem/read_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/main.py"
  }'
```

### 4.2 写文件

```bash
curl -X POST http://localhost:8000/mcp/execute/filesystem/write_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/new_module.py",
    "content": "def hello():\n    print(\"Hello, World!\")"
  }'
```

### 4.3 编辑（带 diff）

```bash
curl -X POST http://localhost:8000/mcp/execute/filesystem/edit_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src/main.py",
    "old_string": "def hello():\n    print(\"hello\")",
    "new_string": "def hello():\n    print(\"Hello, World!\")"
  }'
```

### 4.4 列表目录

```bash
curl -X POST http://localhost:8000/mcp/execute/filesystem/list_directory \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src",
    "include_hidden": false
  }'
```

### 4.5 搜索文件

```bash
# 按 glob
curl -X POST http://localhost:8000/mcp/execute/filesystem/search_files \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "**/*.py",
    "path": "src"
  }'

# 按内容
curl -X POST http://localhost:8000/mcp/execute/filesystem/search_content \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src",
    "pattern": "TODO",
    "file_pattern": "*.py"
  }'
```

### 4.6 批量重命名

```bash
curl -X POST http://localhost:8000/mcp/execute/filesystem/batch_rename \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "src",
    "rules": [
      {"from": "*.jsx", "to": "*.tsx"}
    ],
    "dry_run": true
  }'
```

---

## 五、典型使用流程

### 场景：批量重构 — JSX → TSX

```text
  LLM          Filesystem MCP        项目目录
   │                │                   │
   │  search_files  │                   │
   │  **/*.jsx     │                   │
   ├───────────────▶│                   │
   │                │  glob 扫描         │
   │                ├─────────────────▶│
   │                │  12 个 .jsx       │
   │                │◀─────────────────┤
   │  [file1, ...] │                   │
   │◀───────────────┤                   │
   │                │                   │
   │  read_file    │                   │
   │  file1.jsx    │                   │
   ├───────────────▶│                   │
   │                │  读内容          │
   │                ├─────────────────▶│
   │                │◀─────────────────┤
   │                │                   │
   │  改写为 .tsx   │                   │
   │  write_file   │                   │
   ├───────────────▶│                   │
   │                │  写新文件        │
   │                ├─────────────────▶│
   │                │  file1.tsx       │
   │                │◀─────────────────┤
   │                │                   │
   │  重复 11 次    │                   │
   │                │                   │
   │  或 batch_rename                   │
   ├───────────────▶│                   │
   │                │  一次重命名       │
   │                ├─────────────────▶│
   │                │  12 → 12         │
   │                │◀─────────────────┤
```

### 场景：安全防护 — 越界访问

```text
 LLM            Filesystem MCP           系统
  │                 │                     │
  │  read_file     │                     │
  │  /etc/passwd   │                     │
  ├────────────────▶│                     │
  │                 │  1. 解析绝对路径    │
  │                 │  2. 检查 base_path  │
  │                 │  ❌ 不在 /Users/... │
  │                 │                     │
  │                 │  拒绝 + 审计日志    │
  │                 ├────────────────────▶│
  │                 │                     │
  │ "403 Forbidden:│                     │
  │  out of base"  │                     │
  │◀────────────────┤                     │
```

### 场景：.env 拦截

```text
 LLM            Filesystem MCP           系统
  │                 │                     │
  │  read_file     │                     │
  │  .env.production                     │
  ├────────────────▶│                     │
  │                 │  检查后缀           │
  │                 │  ❌ .env 在黑名单   │
  │                 │                     │
  │ "403 Forbidden:│                     │
  │  .env blocked" │                     │
  │◀────────────────┤                     │
```

---

## 六、安全注意事项

1. **`FILESYSTEM_BASE_PATH` 必须设置**，且越窄越好
2. **绝对路径会被强制改写到 base_path 下**（如 `/etc/passwd` → 拒绝）
3. **`.env` / 密钥文件** 一定要加到 `FILESYSTEM_BLOCKED_EXTENSIONS`
4. **符号链接**：会跟随符号链接，但会校验最终路径仍在 base_path 内
5. **审计**：所有读写操作记录到日志

---

## 七、相关工具

- [Desktop Commander](../后端/Desktop-Commander.md) - 升级版（带 shell）
- [Git](./Git.md) - 文件改动后自动 commit
- [E2B](../测试/E2B.md) - 临时文件可以丢到沙箱

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Desktop-Commander](技术/后端/Desktop-Commander.md)
- [Git](技术/运维/Git.md)

<!-- BACKLINKS END -->
