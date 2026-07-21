# 🔍 Brave Search MCP

> 分类：技术 / 知识库
> 提供方：Brave
> 官网：<https://brave.com/search/api/>
> 适用场景：网页搜索、新闻、博客、教程、图片 / 视频

---

## 一、简介

Brave Search 是不依赖 Google / Bing 的独立搜索引擎，主打**隐私 + 干净结果**。
MCP 集成后，LLM 可以实时联网搜索：
- 最新技术博客
- 新闻事件
- 库 / 框架的 Release Notes
- 公开数据集

> 默认工具数：4

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 网页搜索 | 通用网页结果 |
| 新闻搜索 | 带时间过滤的新闻 |
| 图片搜索 | 缩略图 / 原图 |
| 视频搜索 | YouTube / 其他视频源 |

---

## 三、配置

### 3.1 申请 API Key

1. 打开 <https://brave.com/search/api/>
2. 注册账号 → 选套餐（**免费版 2000 次/月**）
3. Dashboard → 复制 API Key

### 3.2 环境变量

```bash
# 必填
BRAVE_API_KEY=BSAxxxxxxxxxxxxxxxx

# 可选：默认结果数
BRAVE_DEFAULT_COUNT=10

# 可选：默认安全搜索
BRAVE_SAFESEARCH=moderate            # off | moderate | strict

# 可选：默认地区（影响结果地域性）
BRAVE_DEFAULT_COUNTRY=CN             # CN | US | JP | ...

# 可选：默认语言
BRAVE_DEFAULT_LANG=zh-hans
```

---

## 四、使用示例

### 4.1 网页搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/brave_search/web_search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React 19 新特性",
    "count": 10
  }'
```

返回：

```json
{
  "query": "React 19 新特性",
  "results": [
    {
      "title": "React 19 发布说明 - 官方博客",
      "url": "https://react.dev/blog/2024/12/05/react-19",
      "description": "React 19 是 React 历史上最重要的一次发布...",
      "published": "2024-12-05"
    }
  ]
}
```

### 4.2 新闻搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/brave_search/news_search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "OpenAI GPT-5",
    "freshness": "day"
  }'
```

`freshness` 可选：`day` / `week` / `month` / `year`

### 4.3 图片搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/brave_search/image_search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "minimalist dashboard UI design",
    "count": 20
  }'
```

### 4.4 视频搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/brave_search/video_search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Docker tutorial for beginners"
  }'
```

---

## 五、典型使用流程

### 场景：实时联网 — 找最新博客

```text
  用户             LLM           Brave Search MCP      Brave API
   │                │                  │                   │
   │ "FastAPI 最新  │                  │                   │
   │  性能优化"     │                  │                   │
   ├───────────────▶│                  │                   │
   │                │  web_search      │                   │
   │                │  "FastAPI        │                   │
   │                │   performance"   │                   │
   │                ├─────────────────▶│                   │
   │                │                  │  GET /res/v1/web  │
   │                │                  │  /search?q=...    │
   │                │                  ├──────────────────▶│
   │                │                  │◀──────────────────┤
   │                │                  │  10 个结果        │
   │                │  1. 官方博客 v0.110                   │
   │                │  2. GitHub Issue #5234                │
   │                │  3. 知乎专栏                          │
   │                │◀─────────────────┤                   │
   │                │                                  │
   │                │  按发布时间排序                  │
   │                │  + 去重 + 摘要                   │
   │                │                                  │
   │ "以下是 2024 年最值得读的 5 篇…"                  │
   │◀───────────────┤                                  │
```

### 场景：新闻追踪 — 突发热点

```text
  定时任务          LLM           Brave Search MCP
   每 15 分钟            │                  │
       │   news_search   │                  │
       │  "OpenAI GPT"  │                  │
       ├─────────────────▶│                  │
       │                 │  freshness: day │
       │                 ├─────────────────▶│
       │                 │  20 条新闻      │
       │                 │◀─────────────────┤
       │                 │                  │
       │  过滤 + 摘要     │                  │
       │◀────────────────┤                  │
       │                                  │
       │  关键新闻 → Slack/钉钉
```

### 场景：多模态搜索

```text
 LLM         Brave Search MCP           输出
  │               │                     │
  │  image_search│                     │
  │  "极简 dashboard UI"               │
  ├──────────────▶│                     │
  │               │  20 张缩略图        │
  │               │  + 来源             │
  │               │◀────────────────────┤
  │  [图1, 图2..] │                     │
  │◀──────────────┤                     │
  │                                  │
  │  视频教程     │                     │
  │  video_search│                     │
  ├──────────────▶│                     │
  │               │  YouTube 链接      │
  │               │◀────────────────────┤
  │  [v1, v2..]   │                     │
  │◀──────────────┤                     │
```

---

## 六、对比其他搜索

| 引擎 | 特点 |
|------|------|
| **Brave Search** | 隐私优先、无跟踪、独立索引 |
| **Google Custom Search** | 结果最全、但 100 次/天免费 |
| **DuckDuckGo** | 隐私、无 API |
| **Tavily** | 专为 AI 设计、深度爬取 |

如果只选一个，**Brave** 综合最优（免费额度 + 隐私 + 质量）。

---

## 七、注意事项

- **API 限流**：免费版 2000 次/月，1 QPS；高频用付费
- **结果地域性**：设 `BRAVE_DEFAULT_COUNTRY=CN` 拿到国内结果
- **结果质量**：Brave 的中文结果质量略逊于 Google，但隐私性更好
- **图片版权**：商用前确认图片来源的版权
- **反爬**：通过 Brave API 合法获取，不需要自己处理

---

## 八、相关工具

- [Context7](./Context7.md) - 库文档的权威源
- [Docfork](./Docfork.md) - 跨库语义搜索
- [HTTP Client](../后端/HTTP-Client.md) - 也可以直接调其他搜索 API
