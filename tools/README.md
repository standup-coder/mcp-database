# 🛠️ MCP 工具集

> 把所有热门 MCP 用 Markdown 沉淀下来，按"行业 + 技术"两个维度组织。
> 每个 MCP 一份文档，覆盖：简介 / 能力 / 配置 / 示例 / 注意事项 / 相关工具。

---

## 📂 目录结构

```
tools/
├── README.md                 ← 你正在看
├── .env.example              ← 全部 26 个 MCP 的环境变量总模板
│
├── 行业/                     ← 按行业场景分
│   ├── 地图导航/
│   │   └── 高德地图.md
│   ├── 即时通讯/
│   │   └── 钉钉.md
│   ├── 天气/
│   │   └── 天气.md
│   └── 日程管理/
│       └── 日历.md
│
└── 技术/                     ← 按技术角色分
    ├── 前端/
    │   ├── Figma.md
    │   ├── ReactBits.md
    │   └── Browser.md
    ├── 后端/
    │   ├── Database.md
    │   ├── HTTP-Client.md
    │   └── Desktop-Commander.md
    ├── 知识库/
    │   ├── Context7.md
    │   ├── Docfork.md
    │   ├── DeepWiki.md
    │   ├── Memory.md
    │   ├── Sequential-Thinking.md
    │   └── Brave-Search.md
    ├── 测试/
    │   ├── E2B.md
    │   └── Sentry.md
    └── 运维/
        ├── Filesystem.md
        ├── Git.md
        ├── GitHub.md
        ├── Slack.md
        ├── Notion.md
        ├── Linear.md
        ├── Google-Sheets.md
        └── Composio.md
```

**合计 26 个 MCP，每个一份 Markdown。**

---

## 🌐 行业类（4 个）

按业务场景组织，覆盖生活中最常见的几类。

| MCP | 行业 | 一句话 |
|-----|------|--------|
| [高德地图](./行业/地图导航/高德地图.md) | 地图导航 | 路线 / 地理编码 / POI |
| [钉钉](./行业/即时通讯/钉钉.md) | 即时通讯 | 群消息 / 告警 / 卡片 |
| [天气](./行业/天气/天气.md) | 天气 | 实时 / 预报 / 生活指数 |
| [日历](./行业/日程管理/日历.md) | 日程管理 | Google / Outlook / 飞书 / 企微 |

**经典组合**：高德 + 钉钉 = 通勤助手（项目最初的 dumb_mode 模式）

---

## 🛠️ 技术类（22 个）

按技术角色组织，覆盖软件研发的完整链路。

### 🎨 前端（3 个）

| MCP | 一句话 |
|-----|--------|
| [Figma](./技术/前端/Figma.md) | 设计稿布局 / 图片导出 / Token |
| [ReactBits](./技术/前端/ReactBits.md) | 135+ 动画 React 组件源码 |
| [Browser](./技术/前端/Browser.md) | Playwright 浏览器自动化 |

### ⚙️ 后端（3 个）

| MCP | 一句话 |
|-----|--------|
| [Database](./技术/后端/Database.md) | MySQL / PG / SQLite / Redis |
| [HTTP Client](./技术/后端/HTTP-Client.md) | 调任意 HTTP API |
| [Desktop Commander](./技术/后端/Desktop-Commander.md) | 终端命令 / 进程 / 系统信息 |

### 📚 知识库（6 个）

| MCP | 一句话 |
|-----|--------|
| [Context7](./技术/知识库/Context7.md) | 版本精确的库文档注入 |
| [Docfork](./技术/知识库/Docfork.md) | 跨库语义搜索 |
| [DeepWiki](./技术/知识库/DeepWiki.md) | Wiki → 结构化 Markdown |
| [Memory](./技术/知识库/Memory.md) | 持久化知识图谱 |
| [Sequential Thinking](./技术/知识库/Sequential-Thinking.md) | 结构化推理 / 思维链 |
| [Brave Search](./技术/知识库/Brave-Search.md) | 网页 / 新闻 / 图片搜索 |

### 🐛 测试（2 个）

| MCP | 一句话 |
|-----|--------|
| [E2B](./技术/测试/E2B.md) | 云端代码沙箱 |
| [Sentry](./技术/测试/Sentry.md) | 错误监控 / Issue 跟踪 |

### 🖥️ 运维（8 个）

| MCP | 一句话 |
|-----|--------|
| [Filesystem](./技术/运维/Filesystem.md) | 受限的文件操作 |
| [Git](./技术/运维/Git.md) | 版本控制全操作 |
| [GitHub](./技术/运维/GitHub.md) | 仓库 / Issue / PR / Actions |
| [Slack](./技术/运维/Slack.md) | 消息 / Block Kit / 频道 |
| [Notion](./技术/运维/Notion.md) | 页面 / 数据库 / Block |
| [Linear](./技术/运维/Linear.md) | Issue / Cycle / Project |
| [Google Sheets](./技术/运维/Google-Sheets.md) | 表格读写 / 格式化 |
| [Composio](./技术/运维/Composio.md) | 500+ 应用统一集成 |

---

## 🔥 常用组合

| 场景 | 组合 |
|------|------|
| **通勤助手** | 高德 + 钉钉 + 天气 + 日历 |
| **CI 失败告警** | GitHub + Sentry + Slack/钉钉 + Linear |
| **设计稿转代码** | Figma + ReactBits + Browser |
| **故障排查** | Sentry + Sequential Thinking + Database + GitHub |
| **每日天气播报** | 天气 + 钉钉 |
| **数据采集** | HTTP Client + E2B + Google Sheets |
| **知识管理** | Context7 + Docfork + Memory + Notion |
| **LLM 编码工作流** | Sequential Thinking + Context7 + Filesystem + Git + GitHub |

---

## 🚀 快速上手

### 一次性配置所有 MCP

直接用总配置模板：

```bash
cp tools/.env.example .env
# 编辑 .env 填入你的 API Key
```

模板里**全部 26 个 MCP** 的环境变量都列出来了，按 10 个分类组织：
应用/安全、消息通知、地图/天气/日历、文档/知识、设计/前端、数据库/后端、代码/测试、文件/版本控制、协作/管理、异步任务。

每行都标注了：
- `[REQUIRED]` —— 必填
- `[STRONG]` —— 强烈建议（生产环境必须）
- 不标 —— 可选

### 单个 MCP 文档结构

1. **简介** —— 是什么、为什么用
2. **核心能力** —— 能做什么（表格）
3. **配置** —— 环境变量、API Key 申请流程
4. **使用示例** —— curl 调用样例
5. **典型使用流程** —— **ASCII 流程图**，直观展示场景
6. **注意事项** —— 安全 / 限流 / 坑
7. **相关工具** —— 跟谁配合

**读一个文件 5 分钟，跑通一个 30 分钟。**

---

## 📝 维护说明

- 新增 MCP：在 `行业/` 或 `技术/<角色>/` 下新建 `<MCP名称>.md`
- 修改：直接编辑对应 Markdown
- 索引：更新本 README
- 新增环境变量：同步更新 `.env.example`
- 格式：参照已有文件，保持一致
- **每个文档必须包含 ASCII 流程图**

---

## 🪪 License

MIT
