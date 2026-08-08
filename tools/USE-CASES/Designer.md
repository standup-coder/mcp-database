# 🎨 Designer（设计师）MCP 装备清单

> 角色：产品设计师 / UI 设计师 / UX 设计师 / Brand Designer
> 核心工作：界面设计、视觉系统、交互流程、设计交付、设计规范
> 适用 MCP 数：**12 / 26**（14 个不太用 — 设计师是最专一的角色之一）

---

## 📊 总览

| 优先级 | 数量 | 含义 |
|:------:|:----:|------|
| 🟢 重点必备 | 5 | 设计师日常 80% 时间都在用 |
| 🟡 强推 | 4 | 完整设计交付工具链 |
| 🟠 按需 | 3 | 特定场景（动效 / 多端 / 国际化）才上 |
| ⚫ 不推荐 | 14 | 设计师几乎碰不到 |
| **合计** | **26** | tools/ 全部 26 个 MCP |

> 设计师是"工具最专一"的角色 —— 大量 MCP 是工程向的，设计师不需要碰。

---

## 🟢 重点必备（5 个）

| MCP | 路径 | Designer 视角的核心用法 |
|-----|------|----------------------|
| **Figma** | [技术/前端/Figma.md](../技术/前端/Figma.md) | **设计师的主战场**；组件、变体、Auto Layout、设计 Token |
| **ReactBits** | [技术/前端/ReactBits.md](../技术/前端/ReactBits.md) | 动效组件参考；找现成动效启发自己的设计 |
| **Brave Search** | [技术/知识库/Brave-Search.md](../技术/知识库/Brave-Search.md) | 找设计灵感、行业趋势、竞品参考图 |
| **Notion** | [技术/运维/Notion.md](../技术/运维/Notion.md) | 设计规范、Design System 文档、设计走查记录 |
| **Docfork** | [技术/知识库/Docfork.md](../技术/知识库/Docfork.md) | 跨设计系统参考（Material / Ant / Apple HIG） |

---

## 🟡 强推（4 个）

| MCP | 路径 | Designer 视角的用法 |
|-----|------|------------------|
| **Browser** | [技术/前端/Browser.md](../技术/前端/Browser.md) | **看线上效果**、截图竞品、抓动效参考 |
| **Memory** | [技术/知识库/Memory.md](../技术/知识库/Memory.md) | 设计 Token 图谱、组件库版本管理 |
| **Linear** | [技术/运维/Linear.md](../技术/运维/Linear.md) | 设计任务跟踪（"X 页改版"工单）、交付排期 |
| **Sequential Thinking** | [技术/知识库/Sequential-Thinking.md](../技术/知识库/Sequential-Thinking.md) | 复杂设计决策（信息架构、交互流程）拆解 |

---

## 🟠 按需（3 个）

| MCP | 路径 | 用法 |
|-----|------|------|
| **Slack** | [技术/运维/Slack.md](../技术/运维/Slack.md) | 海外团队 / 客户；设计评审通知 |
| **钉钉** | [行业/即时通讯/钉钉.md](../行业/即时通讯/钉钉.md) | 国内团队 / 客户；设计走查通知 |
| **Google Sheets** | [技术/运维/Google-Sheets.md](../技术/运维/Google-Sheets.md) | 设计交付清单、版本记录 |

---

## ⚫ 不推荐（14 个）

| MCP | 路径 | 原因 |
|-----|------|------|
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | ❌ 设计师不直接连数据库 |
| **HTTP Client** | [技术/后端/HTTP-Client.md](../技术/后端/HTTP-Client.md) | ❌ 工程活 |
| **Desktop Commander** | [技术/后端/Desktop-Commander.md](../技术/后端/Desktop-Commander.md) | ❌ 终端命令；设计师不碰 |
| **Filesystem** | [技术/运维/Filesystem.md](../技术/运维/Filesystem.md) | ❌ 本地文件操作 |
| **Git** | [技术/运维/Git.md](../技术/运维/Git.md) | ❌ 用 Figma 协作即可 |
| **GitHub** | [技术/运维/GitHub.md](../技术/运维/GitHub.md) | ❌ 工程师的活 |
| **E2B** | [技术/测试/E2B.md](../技术/测试/E2B.md) | ❌ 跑代码是测试/工程 |
| **Sentry** | [技术/测试/Sentry.md](../技术/测试/Sentry.md) | ❌ 错误监控是工程 |
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | ❌ 同上 |
| **Context7** | [技术/知识库/Context7.md](../技术/知识库/Context7.md) | ❌ 库文档是工程师看的 |
| **DeepWiki** | [技术/知识库/DeepWiki.md](../技术/知识库/DeepWiki.md) | △ 抓公开 Wiki 做参考时偶尔用 |
| **Composio** | [技术/运维/Composio.md](../技术/运维/Composio.md) | ❌ 统一接入平台，设计师无关 |
| **天气** | [行业/天气/天气.md](../行业/天气/天气.md) | ❌ 跟设计无关 |
| **高德地图** | [行业/地图导航/高德地图.md](../行业/地图导航/高德地图.md) | ❌ 跟设计无关（除非做 LBS 产品） |
| **日历** | [行业/日程管理/日历.md](../行业/日程管理/日历.md) | ❌ 用 Linear 排期即可 |

---

## 🔥 实战工作流

### 工作流 1：从用户研究到设计交付

```text
  调研资料           Designer          Brave Search       Notion
  (访谈/数据)            │                  │                │
     │  整理痛点       │                  │                │
     ├─────────────────▶│                  │                │
     │                  │                  │                │
     │                  │  找竞品参考     │                │
     │                  ├─────────────────▶│                │
     │                  │                  │                │
     │                  │  Sequential     │                │
     │                  │  Thinking       │                │
     │                  │  拆解信息架构   │                │
     │                  │                  │                │
     │                  │  Figma 设计稿   │                │
     │                  │  (LLM 帮生成文案)                │
     │                  │                  │                │
     │                  │  ReactBits 参考  │                │
     │                  │  找动效灵感     │                │
     │                  │                  │                │
     │                  │  写 Notion 设计规范              │
     │                  ├─────────────────────────────────▶│
     │                  │  - 颜色         │                │
     │                  │  - 字体         │                │
     │                  │  - 间距         │                │
     │                  │  - 组件         │                │
     │                  │                  │                │
     │                  │  Linear 设计任务 │                │
     │                  │  跟踪交付       │                │
     │                  │                  │                │
     │                  │  Memory 沉淀    │                │
     │                  │  Design Token   │                │
```

### 工作流 2：UI 走查 & 设计验收

```text
  开发完成           Designer          Browser           Linear
     │                  │                │                │
     │  提"走查"请求   │                │                │
     ├─────────────────▶│                │                │
     │                  │                │                │
     │                  │  Browser 打开  │                │
     │                  │  线上环境       │                │
     │                  ├───────────────▶│                │
     │                  │                │  Playwright   │
     │                  │                │  启动浏览器   │
     │                  │                │                │
     │                  │                │  截图         │
     │                  │                ├───────────────┤
     │                  │                │                │
     │                  │  对比 Figma 设计稿              │
     │                  │  (用 Browser 截图 vs Figma 导出)│
     │                  │                │                │
     │                  │  标注差异     │                │
     │                  │                │                │
     │                  │  Linear 建走查 Bug              │
     │                  ├─────────────────────────────────▶│
     │                  │  - 像素差异     │                │
     │                  │  - 间距偏差     │                │
     │                  │  - 颜色不一致   │                │
     │                  │  - 交互问题     │                │
     │                  │                │                │
     │                  │  Notion 走查报告                │
     │                  │  + 截图         │                │
     │                  │                │                │
     │                  │  Memory 沉淀    │                │
     │                  │  "走查常见问题"│                │
```

### 工作流 3：设计系统维护

```text
  设计师              Figma            ReactBits        Notion
     │                  │                │                │
     │  改 Button 组件  │                │                │
     ├─────────────────▶│                │                │
     │                  │                │                │
     │                  │  提取新设计 Token               │
     │                  │  - 颜色         │                │
     │                  │  - 间距         │                │
     │                  │  - 圆角         │                │
     │                  │                │                │
     │                  │  对比 ReactBits │                │
     │                  │  看其他系统的实现│                │
     │                  ├────────────────▶│                │
     │                  │                │                │
     │                  │  Docfork 查     │                │
     │                  │  跨设计系统参考 │                │
     │                  │                │                │
     │                  │  Notion 更新规范│                │
     │                  ├─────────────────────────────────▶│
     │                  │  - 新 Token    │                │
     │                  │  - 迁移指南    │                │
     │                  │                │                │
     │                  │  Linear 通知   │                │
     │                  │  "Button 升级" │                │
     │                  │                │                │
     │                  │  Memory 沉淀   │                │
     │                  │  Design System 版本管理         │
     │                  │  - v1.0         │                │
     │                  │  - v1.1         │                │
     │                  │  - v2.0         │                │
     │                  │  - 迁移路径    │                │
```

---

## 💡 实战建议

1. **Figma 是"唯一"的设计工具** — 别在 Sketch / XD / PS 上花时间了
2. **ReactBits 是动效参考** — 不是让你直接 copy，是找设计灵感
3. **Brave Search 多搜英文资料** — 设计行业英文内容比中文多 5 倍
4. **Docfork 当设计系统 wiki** — 查 Material / Ant / Apple HIG 都行
5. **Notion 写设计规范** — 比 PDF 好维护，比 Figma 好分享
6. **Browser 看线上效果** — 走查必备；截图对比 Figma 是验收核心
7. **Memory 沉淀 Design Token** — 跨项目复用；v1 / v2 / v3 版本管理
8. **Linear 跟工程师对齐** — 别等他们做完才走查，过程就介入
9. **Sequential Thinking 拆解信息架构** — 复杂页面的导航/层级先推理再画
10. **永远不碰 Database / GitHub / E2B** — 那是工程师的活

---

## 🔗 相关工具

- [FDE 装备清单](./FDE.md) — 现场部署视角
- [PM 装备清单](./PM.md) — 产品视角
- [Tech Lead 装备清单](./Tech-Lead.md) — 技术管理视角
- [回到 README 索引](../README.md)
- [总 .env 配置模板](../.env.example)
