# 📊 Data Engineer MCP 装备清单

> 角色：数据工程师 / Data Engineer
> 核心工作：数据 pipeline、ETL、数据建模、数据仓库、数据治理、数据 API
> 适用 MCP 数：**18 / 26**（8 个不太用）

---

## 📊 总览

| 优先级 | 数量 | 含义 |
|:------:|:----:|------|
| 🟢 重点必备 | 5 | DE 日常 80% 时间都在用 |
| 🟡 强推 | 5 | 完整 DE 工具链必备 |
| 🟠 按需 | 8 | 特定场景（前端、ML、客户对接）才上 |
| ⚫ 不推荐 | 8 | DE 几乎碰不到 |
| **合计** | **26** | tools/ 全部 26 个 MCP |

---

## 🟢 重点必备（5 个）

| MCP | 路径 | DE 视角的核心用法 |
|-----|------|------------------|
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | **DE 的主战场**；查 schema、建模型、ETL 写入、慢查询优化 |
| **E2B** | [技术/测试/E2B.md](../技术/测试/E2B.md) | 跑数据脚本、Pandas/Spark 临时分析、隔离沙箱跑脏活 |
| **Google Sheets** | [技术/运维/Google-Sheets.md](../技术/运维/Google-Sheets.md) | 业务数据汇总、对账表、轻量报表；跟业务方对齐最常用 |
| **Memory** | [技术/知识库/Memory.md](../技术/知识库/Memory.md) | **数据字典 / 数据血缘**；表/字段/owner/用途 持久化 |
| **HTTP Client** | [技术/后端/HTTP-Client.md](../技术/后端/HTTP-Client.md) | 调三方 API（CRM、广告平台、SaaS 拉数据）；SSRF 白名单严格配 |

---

## 🟡 强推（5 个）

| MCP | 路径 | DE 视角的用法 |
|-----|------|--------------|
| **Notion** | [技术/运维/Notion.md](../技术/运维/Notion.md) | **数据字典**、pipeline 设计文档、数据治理 SOP |
| **Sequential Thinking** | [技术/知识库/Sequential-Thinking.md](../技术/知识库/Sequential-Thinking.md) | 复杂 pipeline 拆解、ETL 故障推理、建模决策 |
| **Sentry** | [技术/测试/Sentry.md](../技术/测试/Sentry.md) | pipeline 监控、任务失败告警、性能监控 |
| **Context7** | [技术/知识库/Context7.md](../技术/知识库/Context7.md) | 查 dbt / Airflow / Spark 等不熟工具的精确文档 |
| **Linear** | [技术/运维/Linear.md](../技术/运维/Linear.md) | 数据任务 / pipeline 工单跟踪、Sprint 管理 |

---

## 🟠 按需（8 个）

### 客户 / 团队协作

| MCP | 路径 | 用法 |
|-----|------|------|
| **Slack** | [技术/运维/Slack.md](../技术/运维/Slack.md) | 海外团队 / 客户沟通；告警推送 |
| **钉钉** | [行业/即时通讯/钉钉.md](../行业/即时通讯/钉钉.md) | 国内团队 / 客户沟通；告警推送 |
| **GitHub** | [技术/运维/GitHub.md](../技术/运维/GitHub.md) | pipeline 代码管理、PR review、Actions |

### 知识 / 调研

| MCP | 路径 | 用法 |
|-----|------|------|
| **Brave Search** | [技术/知识库/Brave-Search.md](../技术/知识库/Brave-Search.md) | 搜行业数据趋势、最新 ETL 工具、CVE |
| **Docfork** | [技术/知识库/Docfork.md](../技术/知识库/Docfork.md) | 跨工具选型（"哪个 OLAP 引擎适合我的数据量"） |
| **DeepWiki** | [技术/知识库/DeepWiki.md](../技术/知识库/DeepWiki.md) | 抓内部数据 Wiki / 业务文档 |
| **Figma** | [技术/前端/Figma.md](../技术/前端/Figma.md) | 看 BI 报表 / Dashboard 的设计稿 |

### 杂项

| MCP | 路径 | 用法 |
|-----|------|------|
| **Filesystem** | [技术/运维/Filesystem.md](../技术/运维/Filesystem.md) | 受限读 CSV / 日志 dump（替代 Desktop Commander） |
| **Calendar** | [行业/日程管理/日历.md](../行业/日程管理/日历.md) | pipeline 变更窗口、跟团队约评审 |

---

## ⚫ 不推荐（8 个）

| MCP | 路径 | 原因 |
|-----|------|------|
| **Desktop Commander** | [技术/后端/Desktop-Commander.md](../技术/后端/Desktop-Commander.md) | ❌ **DE 几乎不碰 shell**；E2B 跑脚本更安全 |
| **Git** | [技术/运维/Git.md](../技术/运维/Git.md) | ❌ 用 GitHub MCP 即可；DE 很少本地 git 操作 |
| **Browser** | [技术/前端/Browser.md](../技术/前端/Browser.md) | ❌ DE 几乎不碰浏览器自动化 |
| **ReactBits** | [技术/前端/ReactBits.md](../技术/前端/ReactBits.md) | ❌ 前端组件库；DE 跟前端无关 |
| **Composio** | [技术/运维/Composio.md](../技术/运维/Composio.md) | ❌ 统一接入平台，DE 维护没价值；HTTP Client 够用 |
| **Memory** | 在重点必备 | （不是不推荐） |
| **天气** | [行业/天气/天气.md](../行业/天气/天气.md) | ❌ 跟数据工作无关 |
| **高德地图** | [行业/地图导航/高德地图.md](../行业/地图导航/高德地图.md) | ❌ 跟数据工作无关 |

---

## 🔥 实战工作流

### 工作流 1：从三方 API 同步数据到数仓

```text
 客户 CRM          HTTP Client          E2B           Database
  (SaaS API)           │               (ETL)         (数仓)
     │  list_objects   │                │               │
     ├────────────────▶│                │               │
     │                 │  限流 + 重试   │               │
     │                 │  字段映射      │               │
     │                 ├───────────────▶│               │
     │                 │                │  清洗 + 转换 │
     │                 │                │  去重 + 校验 │
     │                 │                │               │
     │                 │                │  bulk_insert │
     │                 │                ├──────────────▶│
     │                 │                │               │
     │                 │                │  Linear 工单 │
     │                 │                │  state: Done │
     │                 │                │               │
     │                 │                │  Memory 沉淀 │
     │                 │                │  crm.users 表 │
     │                 │                │  owner: alice │
```

### 工作流 2：慢查询优化

```text
 业务反馈         Data Engineer       Database MCP         MySQL
  "报表很慢"            │                  │                │
     │                  │                  │                │
     │   拉慢 SQL       │                  │                │
     ├─────────────────▶│                  │                │
     │                  │  解析 + 分组     │                │
     │                  │                  │                │
     │                  │  EXPLAIN 5 个 SQL                │
     │                  ├─────────────────▶│                │
     │                  │                  │  走全表扫描   │
     │                  │                  ├───────────────▶│
     │                  │                  │◀───────────────┤
     │                  │                  │                │
     │                  │  Sequential      │                │
     │                  │  Thinking        │                │
     │                  │  拆解优化方案    │                │
     │                  │                  │                │
     │                  │  ALTER TABLE ADD INDEX              │
     │                  ├─────────────────▶│                │
     │                  │                  │                │
     │                  │ 验证 30s → 0.2s│                │
     │                  │                  │                │
     │                  │  Notion 沉淀     │                │
     │                  │  "索引决策"      │                │
     │                  │                  │                │
     │                  │  Memory 表注释   │                │
     │                  │  "常被 JOIN"     │                │
```

### 工作流 3：数据建模 + 字典管理

```text
 业务需求            LLM              Notion           Memory
     │                │                  │                │
     │ "订单表加     │                  │                │
     │  退款状态"     │                  │                │
     ├───────────────▶│                  │                │
     │                │  拉现有 schema  │                │
     │                │  Database.list_tables              │
     │                │                  │                │
     │                │  Sequential      │                │
     │                │  拆解改动       │                  │
     │                │                  │                │
     │                │  更新 Notion 数据字典              │
     │                ├─────────────────▶│                │
     │                │  Database description             │
     │                │                  │                │
     │                │  Memory 加实体  │                │
     │                │  field:refund_status             │
     │                │  type:enum       │                │
     │                │  owner:data-team │                │
     │                ├───────────────────────────────────▶│
     │                │                  │                │
     │                │  Linear 建工单  │                │
     │                │  DDL 变更        │                │
     │                │  + 数据回填      │                │
     │                │                  │                │
     │ "完成"         │                  │                │
     │◀───────────────┤                  │                │
```

### 工作流 4：数据对账 + 业务汇报

```text
 数仓 (DB)        Data Engineer      Google Sheets       业务方
     │                │                    │                │
     │  查数据       │                    │                │
     │◀───────────────┤                    │                │
     │  3 张表 JOIN │                    │                │
     │                │                    │                │
     │  导出 CSV     │                    │                │
     │  E2B 转换    │                    │                │
     │                │                    │                │
     │                │  写入 Sheets       │                │
     │                ├───────────────────▶│                │
     │                │                    │                │
     │                │  公式 + 图表       │                │
     │                │  =SUMIF(...)      │                │
     │                ├───────────────────▶│                │
     │                │                    │                │
     │                │  通知业务方       │                │
     │                │  Slack/钉钉        │                │
     │                ├───────────────────┼────────────────▶│
     │                │                    │   业务对账     │
     │                │                    │   ✅ 数据一致   │
```

---

## 💡 实战建议

1. **Database 是你"吃饭的家伙"** — 只读账号分析、写账号用 E2B 跑脚本
2. **E2B 替代本地跑 Python** — DE 跑 Pandas/Spark 都在沙箱里，不污染本地
3. **Memory 用来管"数据字典"** — 表/字段/owner/用途/SLA 全部进图谱
4. **Notion 是数据字典的"人类可读版"** — 业务方看 Notion，你用 Memory
5. **Google Sheets 跟业务方对齐** — 别让业务方装 Tableau，Sheets 够用
6. **HTTP Client 调三方 API** — 限流 + 鉴权 + 重试自己实现；SSRF 白名单不能少
7. **Context7 查 dbt / Airflow** — 这些工具版本更新快，别凭记忆写
8. **Sequential Thinking 拆解 pipeline** — 复杂 ETL 不要一上来就写
9. **永远不碰 Desktop Commander** — E2B 跑命令更安全
10. **国内客户/团队 = 钉钉；海外 = Slack** — 别都开

---

## 🔗 相关工具

- [FDE 装备清单](./FDE.md) — 现场部署视角
- [PM 装备清单](./PM.md) — 产品视角
- [SRE 装备清单](./SRE.md) — 运维视角
- [回到 README 索引](../README.md)
- [总 .env 配置模板](../.env.example)
