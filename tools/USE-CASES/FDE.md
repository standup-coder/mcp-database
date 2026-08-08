# 🚀 FDE（Forward Deployed Engineer）MCP 装备清单

> 角色：前沿部署工程师 / 现场 AI 工程师
> 核心工作：把 AI 系统塞进客户的真实环境——读客户数据、接客户系统、跑通客户流程、扛住上线后的问题
> 适用 MCP 数：**24 / 26**（2 个完全不推荐）

---

## 📊 总览

| 优先级 | 数量 | 含义 |
|:------:|:----:|------|
| 🟢 核心必备 | 7 | 任何 FDE 项目起步就要有 |
| 🟡 强烈建议 | 9 | 80% 项目会用到 |
| 🟠 按需选择 | 8 | 特定客户 / 场景才上 |
| ⚫ 完全不推荐 | 2 | FDE 用不到 |
| **合计** | **26** | tools/ 全部 26 个 MCP |

---

## 🟢 核心必备（7 个）

> 第一次去客户现场**只带这 7 个 Key**，缺哪个都会被现场坑。

| MCP | 路径 | 在 FDE 工作流里的核心用法 |
|-----|------|---------------------------|
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | 接客户库（MySQL/PG/Redis），只读账号起步；先 list_tables 把客户 schema 摸清楚 |
| **HTTP Client** | [技术/后端/HTTP-Client.md](../技术/后端/HTTP-Client.md) | 接客户 SaaS API；SSRF 白名单必须配，防止被诱导访问客户内网 |
| **Filesystem** | [技术/运维/Filesystem.md](../技术/运维/Filesystem.md) | 读客户日志、配置文件、dump 文件；路径白名单锁死在项目目录 |
| **Desktop Commander** | [技术/后端/Desktop-Commander.md](../技术/后端/Desktop-Commander.md) | 现场调试、跑迁移脚本、看进程；**最容易出事的 MCP**，严格配置 |
| **Context7** | [技术/知识库/Context7.md](../技术/知识库/Context7.md) | 查客户技术栈里不熟库的精确文档（避免 LLM 凭记忆乱写 API） |
| **Sequential Thinking** | [技术/知识库/Sequential-Thinking.md](../技术/知识库/Sequential-Thinking.md) | 复杂业务逻辑拆解、客户系统排查推理链；现场最有价值的"思维脚手架" |
| **Memory** | [技术/知识库/Memory.md](../技术/知识库/Memory.md) | 客户业务知识图谱（实体/服务/责任人），跨会话保持上下文 |

### 实战工作流：客户接入 PoC

```text
Database ──┐
HTTP Client ─┼─→ 摸清客户环境（schema / API / 文件结构）
Filesystem ─┘
        ↓
Context7 ──→ 查客户技术栈文档
        ↓
Sequential Thinking ──→ 拆解业务逻辑
        ↓
Memory ──→ 沉淀"客户系统理解"到知识图谱
        ↓
Notion ──→ 输出《客户系统接入方案》交付物
```

---

## 🟡 强烈建议（9 个）

### 现场开发 & 部署（5 个）

| MCP | 路径 | 用法 |
|-----|------|------|
| **E2B** | [技术/测试/E2B.md](../技术/测试/E2B.md) | 在客户环境跑迁移脚本、跑脏数据探查；隔离沙箱防止污染客户机器 |
| **Git** | [技术/运维/Git.md](../技术/运维/Git.md) | 本地代码管理；**保护分支 + 禁止 force push** 是底线 |
| **GitHub** | [技术/运维/GitHub.md](../技术/运维/GitHub.md) | 给客户 / 团队提 PR、code review；给客户 demo 时必备 |
| **Browser** | [技术/前端/Browser.md](../技术/前端/Browser.md) | 截图验证 UI 改造、爬客户没有 API 的旧系统、JS 渲染页面抓数据 |
| **Composio** | [技术/运维/Composio.md](../技术/运维/Composio.md) | 客户 SaaS 多到接不过来时，500+ 应用统一接入（**偷懒神器**） |

### 监控 & 排障（1 个）

| MCP | 路径 | 用法 |
|-----|------|------|
| **Sentry** | [技术/测试/Sentry.md](../技术/测试/Sentry.md) | 客户系统错误监控；上线后接 Sentry 是交付"安全感"的关键 |

### 协作 & 沟通（3 个）

| MCP | 路径 | 用法 |
|-----|------|------|
| **Slack** | [技术/运维/Slack.md](../技术/运维/Slack.md) | 海外客户日常沟通、告警推送；Block Kit 卡片能展示带按钮的运维通知 |
| **Linear** | [技术/运维/Linear.md](../技术/运维/Linear.md) | 客户问题 / Feature / Sprint 跟踪；FDE 现场需求流转很重 |
| **Notion** | [技术/运维/Notion.md](../技术/运维/Notion.md) | 客户文档 / 交付物 / 会议纪要协作；**给客户做交付物必备** |
| **Google Sheets** | [技术/运维/Google-Sheets.md](../技术/运维/Google-Sheets.md) | 客户业务数据收集 / 临时报表；客户业务人员最熟悉的工具 |

> 💡 实际是 5+1+4 = 10 个，但 Google Sheets 在协作类里更接近"数据协作"，所以归在协作。

### 实战工作流：现场开发 & 部署

```text
Figma / ReactBits ──→ 前端原型（按需）
        ↓
Filesystem + Git + GitHub ──→ 改代码 + 提交 + 开 PR
        ↓
E2B ──→ 隔离沙箱跑测试
        ↓
Browser ──→ 截图验证 UI
        ↓
Linear ──→ 更新 Sprint 状态
        ↓
Notion ──→ 更新交付物文档
```

### 实战工作流：上线后运维

```text
Sentry ──→ 错误告警
        ↓
Sequential Thinking + Database + GitHub ──→ 排查根因
        ↓
Linear ──→ 建工单跟踪
        ↓
Slack / 钉钉 ──→ 通知客户 + 团队
        ↓
Git / GitHub ──→ 提修复 PR
        ↓
Memory ──→ 把"客户常见坑"沉淀到知识图谱
```

---

## 🟠 按需选择（8 个）

### 客户在国内

| MCP | 路径 | 用法 |
|-----|------|------|
| **钉钉** | [行业/即时通讯/钉钉.md](../行业/即时通讯/钉钉.md) | 国内客户沟通首选；FDE 现场值班时推告警 |
| **高德地图** | [行业/地图导航/高德地图.md](../行业/地图导航/高德地图.md) | 客户做 LBS / 物流 / 配送相关业务时（不然用不到） |
| **日历** | [行业/日程管理/日历.md](../行业/日程管理/日历.md) | 跟国内客户/团队约会议 |

### 设计 / 前端密集

| MCP | 路径 | 用法 |
|-----|------|------|
| **Figma** | [技术/前端/Figma.md](../技术/前端/Figma.md) | 客户有现成设计稿、要还原成代码时 |
| **ReactBits** | [技术/前端/ReactBits.md](../技术/前端/ReactBits.md) | 给客户做 demo / PoC 页面时找现成动效组件 |

### 知识管理

| MCP | 路径 | 用法 |
|-----|------|------|
| **Docfork** | [技术/知识库/Docfork.md](../技术/知识库/Docfork.md) | 不熟客户技术栈时，跨库语义搜索辅助选型 |
| **DeepWiki** | [技术/知识库/DeepWiki.md](../技术/知识库/DeepWiki.md) | 把客户的内部 Wiki / Confluence 转成 LLM 能吃的 MD |
| **Brave Search** | [技术/知识库/Brave-Search.md](../技术/知识库/Brave-Search.md) | 查客户业务领域的最新趋势、新闻、公开资料 |

---

## ⚫ 完全不推荐（2 个）

| MCP | 路径 | 原因 |
|-----|------|------|
| **天气** | [行业/天气/天气.md](../行业/天气/天气.md) | FDE 跟天气业务无关，除非客户就是做天气产品 |
| ❓ 日历 | [行业/日程管理/日历.md](../行业/日程管理/日历.md) | △ 在国内场景有一点点用，但 Linear / Google Calendar 都能替代 |

> 严格说，**只有"天气"**是 FDE 完全用不到的；其他 25 个都有其适用场景。

---

## 🔥 三大典型组合（落地版）

### 组合 1：客户现场接入 PoC（最少配置）

```text
必要 MCP（7 个）：
  Database + HTTP Client + Filesystem        ← 数据接入
  + Desktop Commander                       ← 命令调试
  + Context7 + Sequential Thinking          ← 文档 + 推理
  + Memory                                  ← 客户档案

工作流：
  1. Database.list_tables → 摸清 schema
  2. Filesystem.read_file → 读客户日志
  3. HTTP Client.request → 调客户 API
  4. Context7.query_docs → 查客户技术栈
  5. Sequential Thinking → 拆解业务
  6. Memory.create_entity → 沉淀客户知识
  7. Notion.create_page → 交付物（Notion 是强烈建议）
```

### 组合 2：现场开发 & 部署（标准配置）

```text
必要 MCP（11 个）：上面 7 个 + E2B + Git + GitHub + Browser
强烈建议：Linear + Notion（强烈建议）
按需：Figma / ReactBits

工作流：
  1. Figma.get_layout → 读设计稿
  2. Filesystem.edit_file → 改代码
  3. E2B.execute_code → 跑测试
  4. Browser.screenshot → 验证 UI
  5. Git.commit + Git.push → 提交
  6. GitHub.create_pull_request → 开 PR
  7. Linear.update_issue → 更新状态
  8. Notion.append_blocks → 更新文档
```

### 组合 3：上线后运维（完整配置）

```text
必要 MCP（15 个）：核心 7 + 强烈建议 8
  + Sentry + Slack/钉钉 + Linear + Google Sheets

工作流：
  1. Sentry 触发新 Issue
  2. Sequential Thinking 分步推理
  3. Database 查数据
  4. GitHub 查最近 commit
  5. 定位根因
  6. Linear 建工单
  7. Filesystem 改代码 + Git 提交 + GitHub PR
  8. Slack/钉钉 通知客户
  9. Notion 更新运维周报
 10. Memory 沉淀"客户常见坑"
```

---

## 📊 优先级分布图

```text
 客户接入阶段          现场开发阶段            运维交付阶段
─────────────────    ─────────────         ──────────────
Database ●●●          E2B ●●●               Sentry ●●●
HTTP Client ●●●       Git/GitHub ●●●        Linear ●●●
Filesystem ●●●        Browser ●●            Slack/钉钉 ●●
Desktop Cmd ●●●       Sequential Think ●●●   Notion ●●
Context7 ●●           Memory ●●             Memory ●●
DeepWiki ●            Figma/ReactBits ●     Composio ●
Docfork ●             Composio ●            Google Sheets ●
Memory ●              Google Sheets ●       Brave Search ●
```

> `●●●` 必备 ｜ `●●` 强烈建议 ｜ `●` 按需

---

## 💡 实战建议

1. **第一次去客户现场**只带前 7 个核心必备的 Key，其他按需开通
2. **Desktop Commander 永远最后开**，且必须配 `DESKTOP_BASE_PATH` 白名单 + `DESKTOP_BLOCKED_COMMANDS`
3. **Memory 是 FDE 的"客户档案"**，每个新客户都建一个独立的 entity_id，别混
4. **Notion 是给客户看的，Memory 是给自己用的** — 交付物和内部分开
5. **钉钉 vs Slack 看客户用啥** — 客户用啥你就接啥，别让客户迁就你
6. **Composio 是"偷懒神器"** — 客户 SaaS 多到接不过来时再上，平时维护单独的 MCP 更可控
7. **永远不接"天气"** — 客户问就说没这个 MCP（除非客户就是做天气产品）
8. **Brave Search 是"客户行业调研"利器** — 第一次接触新行业先搜一轮建立 context

---

## 🔗 相关工具

- [回到 README 索引](../README.md)
- [按行业分类的 MCP](../README.md#-行业类-4-个)
- [按技术分类的 MCP](../README.md#-技术类-22-个)
- [总 .env 配置模板](../.env.example)
- [结构化索引](../index.json)
