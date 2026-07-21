# 🧠 Memory MCP（持久化知识图谱）

> 分类：技术 / 知识库
> 适用场景：项目长期记忆、用户偏好、跨会话状态、实体关系

---

## 一、简介

Memory MCP 提供**持久化 + 知识图谱**能力。LLM 可以：
- 记住"用户是前端开发，偏好 React"
- 记录"项目用了 PostgreSQL + Redis"
- 查询"谁负责订单模块"
- 跨会话保持上下文

底层是图数据库（Neo4j / 内存图），实体 + 关系 + 属性。

> 默认工具数：9

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 创建实体 | 带类型、属性 |
| 创建关系 | 实体之间的有向边 |
| 查询实体 | 按 ID / 按类型 / 全文搜索 |
| 更新属性 | 修改实体 / 关系的属性 |
| 删除实体 | 级联删除关系 |
| 图遍历 | 给定实体找 N 度关联 |
| 批量导入 | JSON-LD / CSV 格式 |
| 快照 | 导出整个图 |
| 搜索 | 关键字模糊搜索 |

---

## 三、配置

### 3.1 存储后端

| 后端 | 特点 |
|------|------|
| **SQLite** | 轻量、单机、零依赖 |
| **PostgreSQL** | 团队共享、支持事务 |
| **Neo4j** | 真正图数据库、复杂关系查询 |
| **Redis** | 内存图、快、容量有限 |

### 3.2 环境变量

```bash
# 存储后端
MEMORY_BACKEND=sqlite              # sqlite | postgresql | neo4j | redis
MEMORY_DB_PATH=./data/memory.db    # SQLite 路径

# PostgreSQL
# MEMORY_PG_HOST=localhost
# MEMORY_PG_PORT=5432
# MEMORY_PG_DB=memory
# MEMORY_PG_USER=memory_user
# MEMORY_PG_PASSWORD=xxx

# Neo4j
# MEMORY_NEO4J_URI=bolt://localhost:7687
# MEMORY_NEO4J_USER=neo4j
# MEMORY_NEO4J_PASSWORD=xxx

# 全局配置
MEMORY_MAX_NODES=100000
MEMORY_MAX_DEPTH=5
```

---

## 四、概念模型

```text
实体 (Entity)
  - id
  - type (Person / Project / Library / ...)
  - properties (任意 KV)

关系 (Relation)
  - from (Entity)
  - to (Entity)
  - type (works_on / uses / depends_on)
  - properties
```

---

## 五、使用示例

### 5.1 创建实体

```bash
curl -X POST http://localhost:8000/mcp/execute/memory/create_entity \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "user:alice",
    "type": "Person",
    "properties": {
      "name": "Alice",
      "role": "前端开发",
      "preferences": ["React", "TypeScript", "Tailwind"]
    }
  }'
```

### 5.2 创建关系

```bash
curl -X POST http://localhost:8000/mcp/execute/memory/create_relation \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "user:alice",
    "to": "project:order-system",
    "type": "works_on",
    "properties": {"since": "2024-01-15"}
  }'
```

### 5.3 查询实体

```bash
curl -X POST http://localhost:8000/mcp/execute/memory/get_entity \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"id": "user:alice"}'
```

### 5.4 图遍历

```bash
curl -X POST http://localhost:8000/mcp/execute/memory/traverse \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "user:alice",
    "depth": 2,
    "relation_types": ["works_on", "uses"]
  }'
```

### 5.5 搜索

```bash
curl -X POST http://localhost:8000/mcp/execute/memory/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React",
    "limit": 10
  }'
```

### 5.6 快照 / 恢复

```bash
# 导出
curl -X POST http://localhost:8000/mcp/execute/memory/snapshot \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"format": "json-ld"}'

# 导入
curl -X POST http://localhost:8000/mcp/execute/memory/restore \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @snapshot.json
```

---

## 六、典型使用流程

### 场景：构建项目知识图谱

```text
  LLM                Memory MCP              图数据库
   │                     │                      │
   │  create_entity     │                      │
   │  user:alice (Person)                       │
   ├────────────────────▶│                      │
   │                     │  INSERT              │
   │                     ├─────────────────────▶│
   │                     │◀─────────────────────┤
   │                     │                      │
   │  create_entity     │                      │
   │  project:order-svc (Project)               │
   ├────────────────────▶│                      │
   │                     │                      │
   │  create_relation   │                      │
   │  user:alice --works_on--> project:order-svc│
   ├────────────────────▶│                      │
   │                     │  CREATE EDGE         │
   │                     ├─────────────────────▶│
   │                     │◀─────────────────────┤
   │                     │                      │
   │  create_entity     │                      │
   │  tech:postgres (Tech)                      │
   ├────────────────────▶│                      │
   │                     │                      │
   │  create_relation   │                      │
   │  project:order-svc --uses--> tech:postgres │
   ├────────────────────▶│                      │
```

### 场景：图遍历 — 找"所有用过 PostgreSQL 的项目"

```text
 LLM            Memory MCP                图数据库
  │                 │                       │
  │  traverse      │                       │
  │  start: tech:postgres                   │
  │  relation: uses (反向)                 │
  │  depth: 3                              │
  ├────────────────▶│                       │
  │                 │  MATCH                │
  │                 │  (t:Tech{name:"postgres"})
  │                 │  <-[:uses]- (p:Project)│
  │                 │  <-[:works_on]- (u:Person)│
  │                 │  RETURN u, p, t       │
  │                 ├──────────────────────▶│
  │                 │◀──────────────────────┤
  │                 │  5 个项目，12 个人     │
  │  表格输出       │                       │
  │◀────────────────┤                       │
```

### 场景：跨会话记忆

```text
  昨天会话              Memory MCP         持久化
      │  "我偏好 React"   │                  │
      ├───────────────────▶│                  │
      │                    │  save           │
      │                    ├─────────────────▶│
      │                    │                  │
      │  今天会话          │                  │
      │  "推荐前端框架"    │                  │
      ├───────────────────▶│                  │
      │                    │  load            │
      │                    │  user:alice     │
      │                    │  preferences:    │
      │                    │  [React, TS, ..]│
      │                    ├─────────────────▶│
      │                    │◀─────────────────┤
      │  "基于你的偏好，   │                  │
      │   推荐 React + TS" │                  │
      │◀───────────────────┤                  │
```

### 典型用法

- **个人助手记忆** — 记住用户的偏好、习惯、过往对话
- **项目知识图谱** — 团队成员、服务、依赖关系一目了然
- **客户 / 商机管理** — 客户、联系人、跟进记录
- **学习笔记** — 概念之间的关联（如"X 是 Y 的特例"）

---

## 七、注意事项

- **Schema 设计**：实体 type 最好有固定枚举（Person / Project / Tool ...）
- **重复实体**：用规范化 ID（如 `user:alice` 而不是 `Alice`）
- **图增长**：超过 `MEMORY_MAX_NODES` 时要清理 / 归档
- **隐私**：涉及个人信息需要加密存储 + 访问控制
- **删除级联**：删实体时关系也会删，谨慎

---

## 八、相关工具

- [Notion](../运维/Notion.md) - 人类可读的项目文档
- [Linear](../运维/Linear.md) - 任务 / Issue 结构化记录
- [Context7](./Context7.md) - 库文档可以存为 Memory 里的实体
