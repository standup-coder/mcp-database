# ✍️ Tech Writer（技术文档工程师）MCP 装备清单

> 角色：技术文档工程师 / Tech Writer / 文档负责人
> 核心工作：用户文档、API 文档、教程、FAQ、知识库维护、文档站建设
> 适用 MCP 数：**15 / 26**（11 个不太用）

---

## 📊 总览

| 优先级 | 数量 | 含义 |
|:------:|:----:|------|
| 🟢 重点必备 | 5 | Tech Writer 日常 80% 时间都在用 |
| 🟡 强推 | 5 | 完整文档工具链必备 |
| 🟠 按需 | 5 | 特定场景（国际化 / 视频 / 协作）才上 |
| ⚫ 不推荐 | 11 | Tech Writer 几乎碰不到 |
| **合计** | **26** | tools/ 全部 26 个 MCP |

---

## 🟢 重点必备（5 个）

| MCP | 路径 | Tech Writer 视角的核心用法 |
|-----|------|----------------------|
| **Notion** | [技术/运维/Notion.md](../技术/运维/Notion.md) | **文档协作主战场**；产品手册、教程、内部 wiki |
| **Docfork** | [技术/知识库/Docfork.md](../技术/知识库/Docfork.md) | 跨库语义搜索；查技术栈、查 API、查概念 |
| **DeepWiki** | [技术/知识库/DeepWiki.md](../技术/知识库/DeepWiki.md) | **抓内部 Wiki / Confluence / GitHub Wiki** 转成结构化 MD |
| **Brave Search** | [技术/知识库/Brave-Search.md](../技术/知识库/Brave-Search.md) | 找同类产品文档、用户社区答案、行业术语 |
| **Context7** | [技术/知识库/Context7.md](../技术/知识库/Context7.md) | 查技术栈的精确文档（避免凭记忆写错 API） |

---

## 🟡 强推（5 个）

| MCP | 路径 | Tech Writer 视角的用法 |
|-----|------|------------------|
| **Memory** | [技术/知识库/Memory.md](../技术/知识库/Memory.md) | **术语表 / 命名规范图谱**；跨文档保持一致 |
| **GitHub** | [技术/运维/GitHub.md](../技术/运维/GitHub.md) | 文档 PR review、看 Issue 用户反馈、抓代码示例 |
| **Sequential Thinking** | [技术/知识库/Sequential-Thinking.md](../技术/知识库/Sequential-Thinking.md) | 复杂教程结构、文档信息架构 |
| **Browser** | [技术/前端/Browser.md](../技术/前端/Browser.md) | 截图产品流程、爬公开资料、验证 UI 文案 |
| **Figma** | [技术/前端/Figma.md](../技术/前端/Figma.md) | 导出设计稿作配图、获取 UI 截图 |

---

## 🟠 按需（5 个）

| MCP | 路径 | 用法 |
|-----|------|------|
| **Slack** | [技术/运维/Slack.md](../技术/运维/Slack.md) | 海外团队 / 客户；发布通知、收集反馈 |
| **钉钉** | [行业/即时通讯/钉钉.md](../行业/即时通讯/钉钉.md) | 国内团队 / 客户；同上 |
| **Linear** | [技术/运维/Linear.md](../技术/运维/Linear.md) | 文档任务跟踪、版本规划 |
| **Google Sheets** | [技术/运维/Google-Sheets.md](../技术/运维/Google-Sheets.md) | 翻译记忆库、术语表、文档计划 |
| **Calendar** | [行业/日程管理/日历.md](../行业/日程管理/日历.md) | 文档评审、发布窗口 |

---

## ⚫ 不推荐（11 个）

| MCP | 路径 | 原因 |
|-----|------|------|
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | ❌ 文档工程师不直接连数据库 |
| **HTTP Client** | [技术/后端/HTTP-Client.md](../技术/后端/HTTP-Client.md) | ❌ 工程活 |
| **Desktop Commander** | [技术/后端/Desktop-Commander.md](../技术/后端/Desktop-Commander.md) | ❌ **高风险**；不碰 |
| **Filesystem** | [技术/运维/Filesystem.md](../技术/运维/Filesystem.md) | ❌ 文档用 Notion / Markdown 仓库 |
| **Git** | [技术/运维/Git.md](../技术/运维/Git.md) | ❌ 用 GitHub MCP 即可 |
| **E2B** | [技术/测试/E2B.md](../技术/测试/E2B.md) | ❌ 跑代码是测试/工程 |
| **Sentry** | [技术/测试/Sentry.md](../技术/测试/Sentry.md) | ❌ 错误监控是工程 |
| **ReactBits** | [技术/前端/ReactBits.md](../技术/前端/ReactBits.md) | ❌ 前端组件库，跟写文档无关 |
| **Composio** | [技术/运维/Composio.md](../技术/运维/Composio.md) | ❌ 统一接入平台，文档无关 |
| **天气** | [行业/天气/天气.md](../行业/天气/天气.md) | ❌ 跟文档工作无关 |
| **高德地图** | [行业/地图导航/高德地图.md](../行业/地图导航/高德地图.md) | ❌ 跟文档工作无关 |

---

## 🔥 实战工作流

### 工作流 1：从代码到 API 文档

```text
  源码               Tech Writer      Context7         Docfork
  (GitHub)                │              │                │
     │  读源码          │              │                │
     ├───────────────────▶│              │                │
     │                   │              │                │
     │                   │  查精确文档  │                │
     │                   ├─────────────▶│                │
     │                   │              │                │
     │                   │              │  跨库对比      │
     │                   ├───────────────────────────────▶│
     │                   │              │                │
     │                   │  Sequential  │                │
     │                   │  Thinking    │                │
     │                   │  拆解 API    │                │
     │                   │  章节结构    │                │
     │                   │              │                │
     │                   │  写 Notion   │                │
     │                   │  - endpoint  │                │
     │                   │  - params    │                │
     │                   │  - response  │                │
     │                   │  - examples  │                │
     │                   │              │                │
     │                   │  Memory 沉淀 │                │
     │                   │  术语 / 命名 │                │
     │                   │  保持一致    │                │
     │                   │              │                │
     │                   │  GitHub PR   │                │
     │                   │  文档 review │                │
     │                   │              │                │
     │                   │  发布        │                │
```

### 工作流 2：内部 Wiki → 公开文档

```text
  Confluence        Tech Writer      DeepWiki          Notion
  (内部 Wiki)             │              │                │
     │  抓页面        │              │                │
     ├─────────────────▶│              │                │
     │                  │  fetch_section                  │
     │                  ├─────────────▶│                │
     │                  │              │                │
     │                  │              │  HTML → MD     │
     │                  │              │  清理格式      │
     │                  │              │                │
     │                  │  LLM 改写   │                │
     │                  │  - 去掉内部术语                  │
     │                  │  - 补充示例  │                │
     │                  │  - 加 SEO   │                │
     │                  │              │                │
     │                  │  发布到 Notion                  │
     │                  ├───────────────────────────────▶│
     │                  │              │                │
     │                  │  内部审阅   │                │
     │                  │  Slack 通知 │                │
     │                  │              │                │
     │                  │  GitHub 公开 │                │
     │                  │  docs/ 仓库  │                │
     │                  │              │                │
     │                  │  Memory 沉淀 │                │
     │                  │  "Confluence 抓取模板"          │
```

### 工作流 3：用户反馈 → FAQ 更新

```text
  GitHub Issues     Tech Writer      Brave Search     Notion
  (用户提问)              │              │                │
     │  拉 issues    │              │                │
     │  label:question              │                │
     ├─────────────────▶│              │                │
     │                  │              │                │
     │                  │  搜社区     │                │
     │                  │  已有答案？  │                │
     │                  ├─────────────▶│                │
     │                  │              │                │
     │                  │  Sequential  │                │
     │                  │  Thinking    │                │
     │                  │  - 分类     │                │
     │                  │  - 优先级   │                │
     │                  │              │                │
     │                  │  写 FAQ     │                │
     │                  │  Notion      │                │
     │                  ├───────────────────────────────▶│
     │                  │              │                │
     │                  │  Memory 沉淀 │                │
     │                  │  "高频问题"  │                │
     │                  │              │                │
     │                  │  回 GitHub   │                │
     │                  │  comment     │                │
     │                  │  + doc 链接  │                │
     │                  │              │                │
     │  "问题已解决"   │              │                │
     │◀─────────────────┤              │                │
```

### 工作流 4：教程配图自动化

```text
  教程草稿          Tech Writer      Browser          Figma
     │                  │                │                │
     │  写"X 步骤"     │                │                │
     ├─────────────────▶│                │                │
     │                  │                │                │
     │                  │  打开产品 URL │                │
     │                  ├───────────────▶│                │
     │                  │                │  Playwright   │
     │                  │                │  启动浏览器   │
     │                  │                │                │
     │                  │                │  截图         │
     │                  │                ├───────────────┤
     │                  │                │                │
     │                  │  标注 + 箭头  │                │
     │                  │  (用 Figma)  │                │
     │                  ├─────────────────────────────────▶│
     │                  │                │                │
     │                  │  插入 Notion  │                │
     │                  │  教程页       │                │
     │                  │                │                │
     │                  │  版本管理     │                │
     │                  │  教程更新 → 重新截图             │
```

---

## 💡 实战建议

1. **Notion 是"文档协作默认选项"** — 评审、版本、发布都好用
2. **Docfork 当技术栈 wiki** — 写文档前先查一遍
3. **Context7 查精确 API** — 避免凭记忆写错（最常见的错误）
4. **DeepWiki 抓内部 Wiki** — 转结构化 MD 后统一改写
5. **Brave Search 找社区答案** — GitHub Issues / Reddit / Stack Overflow
6. **Memory 沉淀"术语表"** — 跨文档保持命名一致
7. **GitHub PR review** — 文档跟代码同步更新
8. **Sequential Thinking 拆解复杂教程** — 别一上来就写大纲
9. **Browser 截图配图** — 比手画清晰，比 Figma 快
10. **永远不碰 Database / Desktop Commander / E2B** — 工程活

---

## 🔗 相关工具

- [FDE 装备清单](./FDE.md) — 现场部署视角
- [PM 装备清单](./PM.md) — 产品视角
- [Tech Lead 装备清单](./Tech-Lead.md) — 技术管理视角
- [回到 README 索引](../README.md)
- [总 .env 配置模板](../.env.example)
