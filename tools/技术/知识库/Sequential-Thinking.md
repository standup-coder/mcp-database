# 🧩 Sequential Thinking MCP（结构化推理）

> 分类：技术 / 知识库
> 适用场景：复杂问题分步推理、思维链分支、动态修订思路

---

## 一、简介

Sequential Thinking 不是"知识查询"类 MCP，而是**推理辅助**类。它让 LLM 能：
- 把一个复杂问题拆成 N 步
- 每一步明确标号、记录当前思考
- 在过程中**修订**之前的判断
- 分支尝试多种方案

本质上就是给 LLM 一个"思维脚手架"。

> 默认工具数：1

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 思维编号 | 步号 / 总步数 / 进度 |
| 思路修订 | 标记"之前的判断需要调整" |
| 分支 | 多个并行假设同时探索 |
| 收敛 | 最终得出结论 |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 可选

```bash
SEQUENTIAL_MAX_THOUGHTS=20  # 最大步数
SEQUENTIAL_ALLOW_BRANCHING=true  # 允许分支
SEQUENTIAL_ALLOW_REVISION=true  # 允许修订
SEQUENTIAL_MIN_THOUGHT_LENGTH=50  # 每步最小长度
```

---

## 三、配置

### 3.1 环境变量

```bash
# 单次推理最大步数
SEQUENTIAL_MAX_THOUGHTS=20

# 是否允许分支
SEQUENTIAL_ALLOW_BRANCHING=true

# 是否允许修订（false = 强制线性推理）
SEQUENTIAL_ALLOW_REVISION=true

# 每步最小长度
SEQUENTIAL_MIN_THOUGHT_LENGTH=50
```

> 通常**不需要 API Key**，它是纯计算逻辑。

---

## 四、使用示例

### 4.1 一次完整推理

```bash
curl -X POST http://localhost:8000/mcp/execute/sequential_thinking/sequential_thinking \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "用户问：为什么生产环境 CPU 100%？先列出可能原因：1. 死循环 2. 慢 SQL 3. GC 频繁 4. 流量峰值",
    "thoughtNumber": 1,
    "totalThoughts": 5,
    "nextThoughtNeeded": true
  }'
```

返回：

```json
{
  "thoughtNumber": 1,
  "status": "in_progress",
  "history_length": 1
}
```

### 4.2 第二步

```bash
curl -X POST http://localhost:8000/mcp/execute/sequential_thinking/sequential_thinking \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "收集证据：1. 看 top 进程 2. 看慢 SQL 日志 3. 看 GC 日志",
    "thoughtNumber": 2,
    "totalThoughts": 5,
    "nextThoughtNeeded": true
  }'
```

### 4.3 修订之前的判断

```bash
curl -X POST http://localhost:8000/mcp/execute/sequential_thinking/sequential_thinking \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "等等，我之前假设是死循环，但 top 显示是 mysqld 进程占用 80% CPU，所以应该是慢 SQL。修订：先聚焦慢 SQL。",
    "thoughtNumber": 3,
    "totalThoughts": 5,
    "nextThoughtNeeded": true,
    "isRevision": true,
    "revisesThought": 1
  }'
```

### 4.4 分支探索

```bash
curl -X POST http://localhost:8000/mcp/execute/sequential_thinking/sequential_thinking \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "假设 A：慢 SQL，加索引能解决",
    "thoughtNumber": 4,
    "totalThoughts": 5,
    "nextThoughtNeeded": true,
    "branchFromThought": 3,
    "branchId": "A"
  }'
```

### 4.5 收敛结论

```bash
curl -X POST http://localhost:8000/mcp/execute/sequential_thinking/sequential_thinking \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "最终结论：orders 表 user_id 没加索引，导致全表扫描。修复方案：CREATE INDEX idx_orders_user_id ON orders(user_id)",
    "thoughtNumber": 5,
    "totalThoughts": 5,
    "nextThoughtNeeded": false
  }'
```

---

## 五、典型使用流程

### 场景：故障排查 — 完整推理链

```text
  用户              LLM           Sequential MCP           其他工具
  │                 │                  │                    │
  │ "生产 CPU 100%  │                  │                    │
  │  为什么"        │                  │                    │
  ├────────────────▶│                  │                    │
  │                 │  step 1: 列假设  │                    │
  │                 │  死循环/慢SQL/GC/流量               │
  │                 ├─────────────────▶│                    │
  │                 │                  │                    │
  │                 │  step 2: 收集证据                  │
  │                 ├─────────────────────────────────────▶│
  │                 │  Sentry 看错误 + Database 看慢查询   │
  │                 │  + Desktop Commander top             │
  │                 │◀─────────────────────────────────────┤
  │                 │  mysqld 80% CPU    │                 │
  │                 │  step 3: 修订!     │                 │
  │                 │  isRevision: true  │                 │
  │                 │  revises: step 1   │                 │
  │                 ├─────────────────▶│                    │
  │                 │                  │                    │
  │                 │  step 4A: 加索引  │                    │
  │                 │  branch A         │                    │
  │                 ├─────────────────▶│                    │
  │                 │  step 4B: 限流    │                    │
  │                 │  branch B         │                    │
  │                 ├─────────────────▶│                    │
  │                 │                  │                    │
  │                 │  step 5: 收敛    │                    │
  │                 │  "orders.user_id  │                    │
  │                 │   无索引,加索引"  │                    │
  │                 ├─────────────────▶│                    │
  │ "修复方案:      │                  │                    │
  │  CREATE INDEX…"│                  │                    │
  │◀────────────────┤                  │                    │
```

### 场景：方案选型

```text
 用户              LLM             Sequential MCP         Docfork
  │                 │                   │                    │
  │ "前端框架选型"  │                   │                    │
  ├────────────────▶│                   │                    │
  │                 │  step 1: 列需求   │                    │
  │                 │  SSR/TS/生态/团队 │                    │
  │                 ├──────────────────▶│                    │
  │                 │                   │                    │
  │                 │  step 2: 拉候选  │                    │
  │                 ├───────────────────────────────────────▶│
  │                 │  next.js/remix/astro                  │
  │                 │◀───────────────────────────────────────┤
  │                 │  step 3: 多维评分 │                    │
  │                 ├──────────────────▶│                    │
  │                 │                   │                    │
  │                 │  step 4: 选 next │                    │
  │                 │  nextThought: false                    │
  │                 ├──────────────────▶│                    │
  │ "推荐 Next.js 14"                  │                    │
  │◀────────────────┤                   │                    │
```

### 场景：思维链可视化

```text
  Sequential MCP
       │
       │  记录每一步
       ▼
  ┌──────────────────────────────────┐
  │ Step 1: 假设列表                  │
  │ Step 2: 收集证据  ←─ Sentry       │
  │ Step 3: 修订 step 1 ❌            │
  │ Step 4A: 方案 A  ─┐               │
  │ Step 4B: 方案 B  ─┴─ 并行分支     │
  │ Step 5: 收敛 → 结论               │
  └──────────────────────────────────┘
       │
       │  完整审计日志
       ▼
  事后 review / 团队分享
```

---

## 六、为什么需要它？

LLM 默认输出是"一次性"的长答案，没有结构。Sequential Thinking 强制 LLM：
- **分步**：避免一上来就给结论
- **可追溯**：每一步都记录，方便人审核
- **可修订**：发现错误可以回退 / 改判断
- **可分支**：多个假设并行探索

这在以下场景特别有用：
- 复杂故障排查
- 方案选型（多方案对比）
- 业务逻辑分析
- 数学 / 算法题

---

## 六、与其他 MCP 的组合

| 场景 | 组合 |
|------|------|
| 故障排查 | Sequential + Sentry + Database |
| 选型决策 | Sequential + Docfork + Context7 |
| 学习新库 | Sequential + Context7 + DeepWiki |
| 业务分析 | Sequential + Database + Memory |

---

## 七、注意事项

- **步数控制**：太长浪费 token，太短推理不充分；一般 5~10 步最佳
- **LLM 配合**：要 prompt 工程引导 LLM 真的"用"这个工具，而不是绕过
- **结果可解释**：完整的 thought 序列就是推理日志，可以审计
- **不是万能**：简单问题不需要，反而拖慢响应

---

## 八、相关工具

- [Context7](./Context7.md) - 推理过程中查库文档
- [Database](../后端/Database.md) - 故障排查时拉数据
- [Memory](./Memory.md) - 把推理结论存为知识

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [E2B](技术/测试/E2B.md)
- [Sentry](技术/测试/Sentry.md)

<!-- BACKLINKS END -->
