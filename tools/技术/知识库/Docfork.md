# 📖 Docfork MCP

> 分类：技术 / 知识库
> 官网：<https://docfork.com/>
> 适用场景：跨库语义搜索、文档片段对比、不确定库名时查找

---

## 一、简介

Docfork 收录 9000+ 库，提供**语义搜索**能力。跟 Context7 的区别：
- Context7：你得知道库名（react / django）
- Docfork：用自然语言描述需求，它帮你找最相关的库和文档

例如：
> 搜索 "如何在 Python 里做异步 HTTP 请求"
> Docfork 可能返回：`httpx`、`aiohttp`、`requests-async` 等多个相关库

> 默认工具数：2

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 语义搜索 | 自然语言 → 相关库 + 文档 |
| 跨库对比 | 同时拉多个库的相似 API 文档 |
| 库发现 | 不知道库名时找替代品 |

---

## 三、配置

### 3.1 申请 API Key

1. 打开 <https://docfork.com>
2. 注册 → Dashboard → 创建 API Key

### 3.2 环境变量

```bash
# 必填
DOCFORK_API_KEY=doc_xxxxxxxxxxxxxxxx

# 可选：单次返回结果数
DOCFORK_MAX_RESULTS=10

# 可选：是否包含代码片段
DOCFORK_INCLUDE_CODE=true
```

---

## 四、使用示例

### 4.1 语义搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/docfork/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python 异步 HTTP 客户端，支持 HTTP/2",
    "limit": 5
  }'
```

返回：

```json
{
  "results": [
    {
      "library": "httpx",
      "score": 0.94,
      "description": "A next-generation HTTP client for Python, supporting HTTP/2 and async",
      "snippets": [
        "import httpx\nasync with httpx.AsyncClient() as client:\n    response = await client.get('https://example.com')"
      ]
    },
    {
      "library": "aiohttp",
      "score": 0.87,
      ...
    }
  ]
}
```

### 4.2 跨库对比

```bash
curl -X POST http://localhost:8000/mcp/execute/docfork/compare \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "libraries": ["react", "vue", "svelte"],
    "feature": "component lifecycle hooks"
  }'
```

---

## 五、典型使用流程

### 场景：选型 — 不知道该用哪个库

```text
 用户              LLM             Docfork MCP        Docfork 后端
  │                 │                   │                  │
  │ "Python 异步   │                   │                  │
  │  HTTP 客户端"   │                   │                  │
  ├────────────────▶│                   │                  │
  │                 │  search           │                  │
  │                 │  "Python async    │                  │
  │                 │   HTTP client"    │                  │
  │                 ├──────────────────▶│                  │
  │                 │                   │  语义搜索        │
  │                 │                   ├─────────────────▶│
  │                 │                   │◀─────────────────┤
  │                 │  [httpx: 0.94,   │                  │
  │                 │   aiohttp: 0.87,  │                  │
  │                 │   requests-async  │                  │
  │                 │   : 0.72]         │                  │
  │                 │◀──────────────────┤                  │
  │                 │                                  │
  │                 │  选 httpx (最高分)               │
  │                 │  ↓ 调 Context7 拉精确文档        │
  │                 │  resolve_library "httpx"         │
  │                 │  query_docs ...                  │
  │ "推荐 httpx，HTTP/2 支持好"        │                  │
  │◀────────────────┤                  │                  │
```

### 场景：跨库对比

```text
 LLM              Docfork MCP            3 个库文档
  │                   │                      │
  │  compare          │                      │
  │  [react, vue, svelte]                     │
  │  feature: lifecycle                       │
  ├──────────────────▶│                      │
  │                   │  并发拉取文档         │
  │                   ├─────────────────────▶│
  │                   │                      │
  │                   │  react: useEffect    │
  │                   │  vue: onMounted      │
  │                   │  svelte: onMount     │
  │                   │◀─────────────────────┤
  │                   │                      │
  │  3 套方案对比表   │                      │
  │◀──────────────────┤                      │
```

**Docfork = 选型阶段；Context7 = 实现阶段**。两者配合效果最好。

---

## 六、注意事项

- **API 限流**：免费版 500 次/月
- **语言**：搜索 query 支持中文 + 英文
- **相关性**：搜索结果按相似度排序，可以信赖前 3 条
- **库覆盖**：9000+ 主流库；冷门库可能没有

---

## 七、相关工具

- [Context7](./Context7.md) - 库 ID 已知时的精确文档
- [Brave Search](./Brave-Search.md) - 找最新博客 / 教程
- [Memory](./Memory.md) - 团队内部知识库
