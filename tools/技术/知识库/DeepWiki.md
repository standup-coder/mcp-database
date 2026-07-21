# 📄 DeepWiki MCP

> 分类：技术 / 知识库
> 官网：<https://deepwiki.com/>
> 适用场景：把任意 Wiki / 文档站转换成结构化 Markdown

---

## 一、简介

DeepWiki 把公开的 Wiki、文档站、API Reference 转成**结构化 Markdown**，方便 LLM 阅读。
支持：
- GitHub Wiki
- Confluence（公开页）
- Read the Docs
- 自定义文档站

> 默认工具数：1

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| URL 转 Markdown | 任意文档 URL → 结构化 MD |
| 目录提取 | 自动识别左侧目录树 |
| 代码块保留 | 完整保留原始代码 + 高亮 |
| 链接修复 | 相对路径 → 绝对路径 |

---

## 三、配置

### 3.1 环境变量

```bash
# 可选：缓存目录
DEEPWIKI_CACHE_DIR=./cache/deepwiki

# 可选：缓存过期（秒）
DEEPWIKI_CACHE_TTL=86400            # 1 天

# 可选：最大页面大小
DEEPWIKI_MAX_PAGE_SIZE=2097152      # 2MB

# 可选：UA
DEEPWIKI_USER_AGENT=MCP-DeepWiki/1.0
```

> 通常**不需要 API Key**，DeepWiki 通过抓公开页面工作。

---

## 四、使用示例

### 4.1 转换单个页面

```bash
curl -X POST http://localhost:8000/mcp/execute/deepwiki/fetch \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://react.dev/learn/thinking-in-react"
  }'
```

返回：

```json
{
  "url": "https://react.dev/learn/thinking-in-react",
  "title": "Thinking in React",
  "content": "# Thinking in React\n\nReact is, in our opinion, the best way to build big, fast web apps...",
  "headings": ["Step 1: Break the UI into a component hierarchy", ...],
  "code_blocks": 7
}
```

### 4.2 转换整个目录

```bash
curl -X POST http://localhost:8000/mcp/execute/deepwiki/fetch_section \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://react.dev/learn",
    "max_pages": 20
  }'
```

### 4.3 列出目录

```bash
curl -X POST http://localhost:8000/mcp/execute/deepwiki/list_pages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://react.dev/learn"
  }'
```

---

## 五、典型使用流程

### 场景：批量抓取 React 官方文档作为 RAG 知识库

```text
 文档站         DeepWiki MCP         抓取 + 解析       LLM RAG
 (react.dev)         │                  │              │
     │  fetch_section│                  │              │
     │  /learn       │                  │              │
     ├──────────────▶│                  │              │
     │               │  1. 列目录       │              │
     │               │  2. 逐页抓取    │              │
     │               │  3. HTML → MD   │              │
     │               ├─────────────────▶│              │
     │               │                  │              │
     │               │  20 个 MD 文件  │              │
     │               │◀─────────────────┤              │
     │               │                                  │
     │               │  向量化 + 存向量库              │
     │               ├─────────────────────────────────▶│
     │               │                                  │
 用户问 React 问题                                    │
     │               │                                  │
     ├─────────────────────────────────────────────────▶│
     │               │                                  │
     │   基于真实文档回答（带原文引用）                │
     │◀─────────────────────────────────────────────────┤
```

### 场景：单页快速转 Markdown

```text
  URL            DeepWiki MCP          解析
  文档页             │                  │
     │  fetch       │                  │
     ├──────────────▶│                  │
     │               │  HTTP GET       │
     │               │  → HTML         │
     │               │  → 结构化 MD   │
     │               │  (headings,    │
     │               │   code blocks)  │
     │               ├─────────────────▶│
     │               │◀─────────────────┤
     │  MD 内容     │                  │
     │◀──────────────┤                  │
     │                                  │
     │  喂给 LLM 当上下文              │
```

---

## 六、注意事项

- **抓取限制**：高频访问可能触发站点的反爬（429）
- **登录内容**：只支持公开页面，私有 Wiki 抓不到
- **动态渲染**：JS 渲染的 SPA（React/Vue 写的文档站）需要预渲染，框架会用 Browser MCP 兜底
- **版权**：抓取的内容仅供个人 / 团队学习使用，不要公开发布

---

## 七、相关工具

- [Context7](./Context7.md) - 库文档的"权威源"
- [Docfork](./Docfork.md) - 跨库语义搜索
- [Memory](./Memory.md) - 把抓取的内容存到知识图谱
- [Browser](../前端/Browser.md) - JS 渲染页面的备选
