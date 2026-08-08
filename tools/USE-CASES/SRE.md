# 🛡️ SRE / DevOps MCP 装备清单

> 角色：SRE / DevOps 工程师
> 核心工作：系统稳定性保障、故障响应、监控告警、容量规划、值班 oncall
> 适用 MCP 数：**20 / 26**（6 个不太用）

---

## 📊 总览

| 优先级 | 数量 | 含义 |
|:------:|:----:|------|
| 🟢 重点必备 | 5 | SRE 日常 oncall + 故障排查离不了 |
| 🟡 强推 | 7 | 完整 SRE 工具链必备 |
| 🟠 按需 | 8 | 特定场景（海外、CI 调优）才上 |
| ⚫ 不推荐 | 6 | 几乎用不到 |
| **合计** | **26** | tools/ 全部 26 个 MCP |

---

## 🟢 重点必备（5 个）

| MCP | 路径 | SRE 视角的核心用法 |
|-----|------|------------------|
| **Sentry** | [技术/测试/Sentry.md](../技术/测试/Sentry.md) | 错误监控、Issue 跟踪、性能分析；**SRE 的雷达** |
| **Desktop Commander** | [技术/后端/Desktop-Commander.md](../技术/后端/Desktop-Commander.md) | 服务器命令、进程管理、查日志、跑诊断脚本；**最强大也最危险** |
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | 慢查询分析、表结构、备份恢复；线上排查必备 |
| **GitHub** | [技术/运维/GitHub.md](../技术/运维/GitHub.md) | 看 PR、查 commit、找"哪个版本引入的 bug"、Actions 状态 |
| **钉钉** | [行业/即时通讯/钉钉.md](../行业/即时通讯/钉钉.md) | **告警推送首选**；国内 oncall 全靠它 |

---

## 🟡 强推（7 个）

| MCP | 路径 | SRE 视角的用法 |
|-----|------|--------------|
| **Filesystem** | [技术/运维/Filesystem.md](../技术/运维/Filesystem.md) | 受限读日志、查配置；比 Desktop Commander 安全 |
| **HTTP Client** | [技术/后端/HTTP-Client.md](../技术/后端/HTTP-Client.md) | 调监控 API、查云厂商健康端点（白名单严格） |
| **Memory** | [技术/知识库/Memory.md](../技术/知识库/Memory.md) | 运维知识图谱：服务依赖、负责人、常见故障模式 |
| **Sequential Thinking** | [技术/知识库/Sequential-Thinking.md](../技术/知识库/Sequential-Thinking.md) | 复杂故障的推理链（不只是套命令）；oncall 复盘神器 |
| **E2B** | [技术/测试/E2B.md](../技术/测试/E2B.md) | 跑诊断脚本、数据采样、临时分析；隔离沙箱保护主机 |
| **Slack** | [技术/运维/Slack.md](../技术/运维/Slack.md) | 海外告警、客户沟通；Block Kit 做交互式告警 |
| **Notion** | [技术/运维/Notion.md](../技术/运维/Notion.md) | 运维 Runbook、故障复盘文档、SOP 沉淀 |

---

## 🟠 按需（8 个）

### 海外告警

| MCP | 路径 | 用法 |
|-----|------|------|
| **Slack** | 已在强推 | 跟钉钉二选一，看客户/团队用啥 |
| **Linear** | [技术/运维/Linear.md](../技术/运维/Linear.md) | 故障 / 改进工单跟踪、值班排班 |

### 监控 / 容量

| MCP | 路径 | 用法 |
|-----|------|------|
| **Google Sheets** | [技术/运维/Google-Sheets.md](../技术/运维/Google-Sheets.md) | 容量规划表、值班表、季度指标 |
| **Brave Search** | [技术/知识库/Brave-Search.md](../技术/知识库/Brave-Search.md) | 查 CVE、技术博客、最新事故复盘 |

### 文档 / 知识

| MCP | 路径 | 用法 |
|-----|------|------|
| **Context7** | [技术/知识库/Context7.md](../技术/知识库/Context7.md) | 查不熟服务的精确文档（K8s operator、PromQL 等） |
| **Docfork** | [技术/知识库/Docfork.md](../技术/知识库/Docfork.md) | 跨工具选型（如"哪个 K8s ingress 更好"） |
| **DeepWiki** | [技术/知识库/DeepWiki.md](../技术/知识库/DeepWiki.md) | 把内部 Wiki / Confluence 转成 LLM 可读 |

### 行业场景

| MCP | 路径 | 用法 |
|-----|------|------|
| **日历** | [行业/日程管理/日历.md](../行业/日程管理/日历.md) | 排值班表、oncall 轮转、变更窗口 |
| **高德地图** | [行业/地图导航/高德地图.md](../行业/地图导航/高德地图.md) | 多机房地理容灾演练时 |

---

## ⚫ 不推荐（6 个）

| MCP | 路径 | 原因 |
|-----|------|------|
| **Figma** | [技术/前端/Figma.md](../技术/前端/Figma.md) | ❌ 设计的活，SRE 几乎不碰 |
| **ReactBits** | [技术/前端/ReactBits.md](../技术/前端/ReactBits.md) | ❌ 前端组件库；跟 SRE 无关 |
| **Browser** | [技术/前端/Browser.md](../技术/前端/Browser.md) | ❌ 截图 / 爬虫是前端/QA 的活 |
| **Notion** | 在强推里 | （不是不推荐） |
| **Composio** | [技术/运维/Composio.md](../技术/运维/Composio.md) | ❌ 统一接入平台，SRE 维护没价值；单独 MCP 更可控 |
| **天气** | [行业/天气/天气.md](../行业/天气/天气.md) | ❌ 跟运维无关 |

---

## 🔥 实战工作流

### 工作流 1：oncall 故障响应

```text
 Sentry 告警       SRE oncall         Sequential       Desktop
   │                 │                Thinking          Commander
   │  P0 新增        │                │                  │
   ├────────────────▶│                │                  │
   │                 │  拉详情        │                  │
   │                 │  + 堆栈        │                  │
   │                 │                │                  │
   │                 │  Step 1: 列假设                  │
   │                 ├───────────────▶│                  │
   │                 │  - 流量突增                      │
   │                 │  - 慢 SQL                       │
   │                 │  - 内存泄漏                     │
   │                 │                │                  │
   │                 │  Step 2: 收集证据                │
   │                 ├─────────────────────────────────▶│
   │                 │                │   top / iostat  │
   │                 │                │   tail log      │
   │                 │                │                  │
   │                 │  Step 3: 定位  │                  │
   │                 │  "mysqld 80% CPU"                │
   │                 │                │                  │
   │                 │  Database 慢查询                 │
   │                 ├───────────────▶│                  │
   │                 │                │                  │
   │                 │  通知团队      │                  │
   │                 │  钉钉群         │                  │
   │                 ├───────────────▶│                  │
   │                 │                │  @负责人         │
   │                 │                │  + 故障链接      │
   │                 │                │                  │
   │                 │  Linear 建工单 │                  │
   │                 ├───────────────▶│                  │
   │                 │  ENG-789: "降级"                  │
   │                 │                │                  │
   │                 │  GitHub hotfix │                  │
   │                 ├───────────────▶│                  │
   │                 │                │  PR + auto-merge│
   │                 │                │                  │
   │                 │  Notion 复盘   │                  │
   │                 ├───────────────▶│                  │
   │                 │                │  RCA 文档       │
   │                 │                │                  │
   │                 │  Memory 沉淀   │                  │
   │                 ├───────────────▶│                  │
   │                 │                │  "orders.user_id│
   │                 │                │   索引易丢"     │
```

### 工作流 2：定期巡检

```text
 Cron 任务        SRE 机器人         Desktop Cmd      钉钉/Slack
  每日 09:00           │                │                │
     │  health_check  │                │                │
     ├────────────────▶│                │                │
     │                 │                │                │
     │                 │  1. df -h     │                │
     │                 ├───────────────▶│                │
     │                 │                │                │
     │                 │  2. docker ps │                │
     │                 ├───────────────▶│                │
     │                 │                │                │
     │                 │  3. top       │                │
     │                 ├───────────────▶│                │
     │                 │                │                │
     │                 │  4. 数据库连接数                 │
     │                 ├───────────────▶│                │
     │                 │                │                │
     │                 │  汇总 + 摘要  │                │
     │                 │                │                │
     │                 │  send_markdown│                │
     │                 ├─────────────────────────────────▶│
     │                 │                │   #ops-daily   │
     │                 │                │   ┌────────┐   │
     │                 │                │   │今日健康 │   │
     │                 │                │   │磁盘 45% │   │
     │                 │                │   │CPU 30%  │   │
     │                 │                │   │连接 120 │   │
     │                 │                │   │[详情]   │   │
     │                 │                │   └────────┘   │
```

### 工作流 3：变更发布

```text
 工程师              SRE              GitHub           Linear
   │                 │                  │                │
   │ "今天 14:00 上线 v1.2.3"            │                │
   ├────────────────▶│                  │                │
   │                 │                  │                │
   │                 │  review PR       │                │
   │                 ├─────────────────▶│                │
   │                 │                  │                │
   │                 │  check CI        │                │
   │                 ├─────────────────▶│                │
   │                 │                  │                │
   │                 │  approve + merge │                │
   │                 ├─────────────────▶│                │
   │                 │                  │                │
   │                 │  trigger Actions │                │
   │                 ├─────────────────▶│                │
   │                 │                  │                │
   │                 │  Linear 更新     │                │
   │                 ├───────────────────────────────────▶│
   │                 │  state: Done    │                │
   │                 │                  │                │
   │                 │  监控 30 min    │                │
   │                 │  异常 → 回滚    │                │
   │                 │                  │                │
   │                 │  Notion 更新     │                │
   │                 │  release notes  │                │
```

---

## 💡 实战建议

1. **Sentry 是你"晚上睡觉"的安全感** — 告警没配好就别下班
2. **Desktop Commander 配得越严越好** — `BLOCKED_COMMANDS` 一定要有 `rm -rf /`、`shutdown`、`dd`
3. **Database 用只读账号** — SRE 也别拿 root 连生产；`DB_ALLOW_WRITE=false`
4. **Memory 沉淀"故障模式"** — 每次 oncall 后把"常见坑"写进图谱（索引易丢、连接池满...）
5. **Sequential Thinking + Sentry 是黄金组合** — Sentry 给数据，Sequential 帮推理
6. **E2B 跑诊断脚本** — 不要在生产机器上直接跑测试代码
7. **国内 oncall = 钉钉；海外 oncall = Slack** — 二选一就行，别都开
8. **Notion 写 Runbook** — 新人 oncall 第一件事是翻 Runbook
9. **Linear 不是给 PM 的** — 故障 / 改进工单是 SRE 的；别让 PM 把它当 Issue 池
10. **永远不碰 Figma / ReactBits / Browser** — 那是前端/QA 的活

---

## 🔗 相关工具

- [FDE 装备清单](./FDE.md) — 现场部署视角
- [PM 装备清单](./PM.md) — 产品视角
- [回到 README 索引](../README.md)
- [总 .env 配置模板](../.env.example)
