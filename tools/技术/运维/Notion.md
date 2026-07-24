# 📝 Notion MCP

> 分类：技术 / 运维
> 官网：<https://www.notion.so/>
> 适用场景：知识库、文档协作、数据库、Wiki、项目管理

---

## 一、简介

Notion MCP 把 Notion API 暴露给 LLM。LLM 可以：
- 读 / 写 Page
- 管理 Database（CRUD 行、查询、过滤）
- 改 Block（段落、列表、代码块、表格）
- 搜索
- 评论

适用：技术文档、产品需求、会议记录、数据库管理。

> 默认工具数：7

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 页面 CRUD | 读 / 创建 / 修改 / 归档 |
| Block 操作 | 增 / 删 / 改 / 顺序 |
| Database 操作 | 查行、插行、改行、过滤 |
| 搜索 | 标题 / 内容 |
| 评论 | 读 / 写 |
| 用户 | 查询 |
| 模板 | 用模板建页 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxx  # Internal Integration Token
```

### 可选

```bash
NOTION_API_VERSION=2022-06-28  # API 版本
NOTION_DEFAULT_PARENT_PAGE_ID=xxx  # 默认父页面
```

---

## 三、配置

### 3.1 创建 Integration

1. 打开 <https://www.notion.so/my-integrations>
2. "Create new integration"
3. 命名 + 选工作区
4. Capabilities 勾选：Read / Update / Insert content、Read user info
5. 复制 **Internal Integration Token**（`secret_` 开头）

### 3.2 分享页面

⚠️ **Notion 的权限模型是"先邀请后访问"**：

1. 在 Notion 里打开要管理的页面
2. 右上角 "..." → "Connections" → 添加你的 Integration
3. 子页面会自动继承权限

### 3.3 环境变量

```bash
# 必填
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxx

# 可选：Notion 版本
NOTION_API_VERSION=2022-06-28

# 可选：默认父页面
NOTION_DEFAULT_PARENT_PAGE_ID=xxx
```

---

## 四、使用示例

### 4.1 搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/notion/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "技术评审",
    "filter": {"property": "object", "value": "page"}
  }'
```

### 4.2 读页面

```bash
curl -X POST http://localhost:8000/mcp/execute/notion/get_page \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "page_id": "abc123-def456"
  }'
```

### 4.3 创建页面

```bash
curl -X POST http://localhost:8000/mcp/execute/notion/create_page \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "page_id", "page_id": "abc123"},
    "properties": {
      "title": {
        "title": [{"text": {"content": "新页面"}}]
      }
    },
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
          "rich_text": [{"type": "text", "text": {"content": "标题"}}]
        }
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"type": "text", "text": {"content": "正文内容"}}]
        }
      }
    ]
  }'
```

### 4.4 追加 Block

```bash
curl -X POST http://localhost:8000/mcp/execute/notion/append_blocks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "page_id": "abc123",
    "blocks": [
      {
        "object": "block",
        "type": "code",
        "code": {
          "rich_text": [{"type": "text", "text": {"content": "print(\"hello\")"}}],
          "language": "python"
        }
      }
    ]
  }'
```

### 4.5 Database 查询

```bash
curl -X POST http://localhost:8000/mcp/execute/notion/query_database \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "database_id": "db_xxx",
    "filter": {
      "property": "Status",
      "select": {"equals": "In Progress"}
    },
    "sorts": [
      {"property": "Priority", "direction": "descending"}
    ]
  }'
```

### 4.6 Database 插入行

```bash
curl -X POST http://localhost:8000/mcp/execute/notion/create_database_row \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "database_id": "db_xxx",
    "properties": {
      "Name": {"title": [{"text": {"content": "新任务"}}]},
      "Status": {"select": {"name": "Todo"}},
      "Priority": {"select": {"name": "High"}}
    }
  }'
```

---

## 五、典型使用流程

### 场景：会议纪要自动归档

```text
  会议结束         LLM            Notion MCP         Notion API
     │               │                │                  │
     │  "整理纪要"   │                │                  │
     ├──────────────▶│                │                  │
     │               │  1. 总结要点  │                  │
     │               │  2. 提取决策  │                  │
     │               │  3. 提取待办  │                  │
     │               │                │                  │
     │               │  append_blocks │                  │
     │               ├───────────────▶│                  │
     │               │                │  找 "会议纪要"  │
     │               │                │  父页面         │
     │               │                ├─────────────────▶│
     │               │                │  search 父页   │
     │               │                │◀─────────────────┤
     │               │                │                  │
     │               │                │  PATCH block    │
     │               │                │  + 新 Block     │
     │               │                ├─────────────────▶│
     │               │                │                  │
     │               │                │  ✅ 写入完成     │
     │               │                │◀─────────────────┤
     │               │                │                  │
     │               │  add_comment   │                  │
     │               │  @相关人        │                  │
     │               ├───────────────▶│                  │
     │ "已归档 + @ 3 人"               │                  │
     │◀──────────────┤                │                  │
```

### 场景：GitHub Issue 同步到 Notion Database

```text
 GitHub MCP        LLM            Notion MCP         Notion DB
     │               │                │                  │
     │  list_issues  │                │                  │
     ├──────────────▶│                │                  │
     │  [issue1, 2, 3]                │                  │
     │◀──────────────┤                │                  │
     │               │                │                  │
     │               │  转换格式       │                  │
     │               │  GitHub → Notion DB 属性         │
     │               │                │                  │
     │               │  create_database_row × 3          │
     │               ├───────────────▶│                  │
     │               │                │  POST /pages     │
     │               │                ├─────────────────▶│
     │               │                │  row 1, 2, 3    │
     │               │                │◀─────────────────┤
     │               │                │                  │
     │  update_issue (comment: 同步到 Notion #db)        │
     ├──────────────▶│                │                  │
     │  ✅ 同步完成  │                │                  │
```

### 场景：批量文档生成

```text
 LLM            Notion MCP             Notion
  │                 │                    │
  │  模板: PRD       │                    │
  │  数据: 需求列表  │                    │
  │                 │                    │
  │  循环 5 个需求   │                    │
  │  create_page    │                    │
  │  + 模板 Block   │                    │
  ├────────────────▶│                    │
  │                 │  5 个新页面        │
  │                 ├───────────────────▶│
  │                 │  /PRD/             │
  │                 │    1. 登录        │
  │                 │    2. 注册        │
  │                 │    3. 找回密码    │
  │                 │    4. 第三方登录  │
  │                 │    5. 2FA         │
  │                 │◀───────────────────┤
  │  5 个页面 + 侧边栏目录              │
```

---

## 六、注意事项

- **API 限流**：3 req/s，平均 200ms 一次
- **Block 嵌套**：可嵌套子 block，但深度限制 2 层
- **文件上传**：通过外部 URL 引用，**不能直接上传二进制**
- **公式 / Rollup**：复杂字段类型 query 较慢
- **权限**：Integration 默认看不到私有页面，必须先分享

---

## 七、对比

| 维度 | Notion | Confluence | 飞书文档 |
|------|--------|-----------|----------|
| **API 易用性** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Block 模型** | 树形 | 存储过程 | 富文本 |
| **数据库** | ⭐⭐⭐⭐⭐ | 弱 | 强 |
| **协作** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **价格** | 免费版够小团队 | 企业版贵 | 国内友好 |

---

## 八、相关工具

- [GitHub](./GitHub.md) - Issue / PR 内容同步
- [Linear](./Linear.md) - 任务管理替代
- [Google Sheets](./Google-Sheets.md) - 结构化数据补充
- [Memory](../知识库/Memory.md) - 把 Notion 知识存到图谱

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Figma](技术/前端/Figma.md)
- [Memory](技术/知识库/Memory.md)
- [Composio](技术/运维/Composio.md)
- [Google-Sheets](技术/运维/Google-Sheets.md)
- [Linear](技术/运维/Linear.md)

<!-- BACKLINKS END -->
