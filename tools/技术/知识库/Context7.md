# 📚 Context7 MCP

> 分类：技术 / 知识库
> 官网：<https://context7.com/>
> 适用场景：版本精确的库文档注入、解决 LLM 知识过时问题

---

## 一、简介

Context7 把**最新的、版本精确的**库文档直接喂给 LLM。解决经典问题：
> "LLM 训练数据停留在一年前，写出来的 API 用法早就过时了"

Context7 收录 9000+ 流行库（React、Vue、Django、FastAPI、Next.js 等），每次请求时**按当前版本**返回文档片段，作为上下文塞给 LLM。

> 默认工具数：2

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 库 ID 解析 | `react` → `/facebook/react` |
| 文档查询 | 关键字 → 文档片段（带版本号） |
| 主题过滤 | Hooks / Components / API / Migration 等 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 可选

```bash
CONTEXT7_API_KEY=ctx7_xxxxxxxx  # 无 Key 也能用（限流）
CONTEXT7_MAX_SNIPPETS=5  # 单次返回片段数
```

---

## 三、配置

### 3.1 申请 API Key

1. 打开 <https://context7.com/dashboard>
2. 注册账号 → 创建 API Key
3. 免费版足够个人使用

### 3.2 环境变量

```bash
# 可选：API Key（无 Key 也能用，但有限流）
CONTEXT7_API_KEY=ctx7_xxxxxxxx

# 可选：单次返回片段数
CONTEXT7_MAX_SNIPPETS=5

# 可选：默认版本
# CONTEXT7_DEFAULT_VERSION=18.2.0
```

---

## 四、使用示例

### 4.1 解析库 ID

```bash
curl -X POST http://localhost:8000/mcp/execute/context7/resolve_library \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"libraryName": "react"}'
```

返回：

```json
{
  "libraryId": "/facebook/react",
  "name": "React",
  "versions": ["18.3.1", "18.2.0", "17.0.2"]
}
```

### 4.2 查询文档

```bash
curl -X POST http://localhost:8000/mcp/execute/context7/query_docs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "libraryId": "/facebook/react",
    "query": "useEffect cleanup function",
    "version": "18.2.0",
    "topic": "hooks"
  }'
```

返回（简化）：

```json
{
  "library": "React 18.2.0",
  "topic": "useEffect",
  "snippets": [
    {
      "title": "useEffect with cleanup",
      "code": "useEffect(() => {\n  const subscription = source.subscribe();\n  return () => subscription.unsubscribe();\n}, [source]);",
      "explanation": "返回的函数会在组件卸载或依赖更新前调用..."
    }
  ]
}
```

---

## 五、典型使用流程

### 场景：用 Context7 让 LLM 写"最新版本"代码

```text
 用户              LLM             Context7 MCP        Context7 后端
  │                 │                   │                   │
  │ "用 useEffect  │                   │                   │
  │  做清理"        │                   │                   │
  ├────────────────▶│                   │                   │
  │                 │  resolve_library  │                   │
  │                 │  "react"          │                   │
  │                 ├──────────────────▶│                   │
  │                 │                   │  /facebook/react  │
  │                 │                   │  v18.2.0          │
  │                 │◀──────────────────┤                   │
  │                 │  query_docs       │                   │
  │                 │  useEffect cleanup│                   │
  │                 │  v18.2.0          │                   │
  │                 ├──────────────────▶│                   │
  │                 │                   │  检索文档片段     │
  │                 │                   ├──────────────────▶│
  │                 │                   │◀──────────────────┤
  │                 │  snippet + code   │                   │
  │                 │◀──────────────────┤                   │
  │                 │                                   │
  │                 │  组装 prompt:                    │
  │                 │  [system: 你是 React 专家]        │
  │                 │  + [Context7 真实文档]            │
  │                 │  + [用户问题]                    │
  │                 │                                   │
  │ "正确代码 + cleanup 解释"         │                   │
  │◀────────────────┤                  │                   │
```

### 场景：版本兼容性检查

```text
 LLM            Context7 MCP           库版本
  │                  │                  │
  │  resolve_library │                  │
  ├─────────────────▶│                  │
  │                  │  /vercel/next.js│
  │                  │  v14, v13, v12   │
  │◀─────────────────┤                  │
  │                  │                  │
  │  query_docs      │                  │
  │  "server actions"│                  │
  │  v14             │                  │
  ├─────────────────▶│                  │
  │  文档片段        │                  │
  │◀─────────────────┤                  │
  │                  │                  │
  │  query_docs      │                  │
  │  "server actions"│                  │
  │  v13             │                  │
  ├─────────────────▶│                  │
  │  文档片段 (无此功能)               │
  │◀─────────────────┤                  │
  │                  │                  │
  │ "Server Actions 是 Next 14 引入的"  │
```

这样 LLM 写出来的代码就是**当前版本正确**的，而不是凭"记忆"乱写。

---

## 六、对比其他文档 MCP

| 工具 | 特点 |
|------|------|
| **Context7** | 库文档 + 版本精确 |
| **Docfork** | 跨库语义搜索（不挑版本） |
| **DeepWiki** | Wiki 文档 → 结构化 Markdown |
| **Memory** | 自定义知识库 / 知识图谱 |

四者互补，可同时使用。

---

## 七、注意事项

- **库覆盖**：9000+ 主流库，但小众库可能搜不到
- **版本**：默认返回最新版本；要锁定版本用 `version` 参数
- **语言**：英文文档为主；中文社区翻译版本部分支持
- **限流**：免费版 1000 次/月；频繁用建议付费
- **Code Snippet 长度**：单片段上限 5000 字符，超长文档会截断

---

## 八、相关工具

- [Docfork](./Docfork.md) - 跨库语义搜索
- [DeepWiki](./DeepWiki.md) - Wiki 类文档转换
- [Memory](./Memory.md) - 自己项目内的知识图谱

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [ReactBits](技术/前端/ReactBits.md)
- [Brave-Search](技术/知识库/Brave-Search.md)
- [DeepWiki](技术/知识库/DeepWiki.md)
- [Docfork](技术/知识库/Docfork.md)
- [Memory](技术/知识库/Memory.md)
- [Sequential-Thinking](技术/知识库/Sequential-Thinking.md)

<!-- BACKLINKS END -->
