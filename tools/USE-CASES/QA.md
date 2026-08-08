# 🧪 QA / 测试工程师 MCP 装备清单

> 角色：QA / 测试工程师 / SDET
> 核心工作：测试用例设计、自动化测试、Bug 复现、回归测试、性能测试
> 适用 MCP 数：**18 / 26**（8 个不太用）

---

## 📊 总览

| 优先级 | 数量 | 含义 |
|:------:|:----:|------|
| 🟢 重点必备 | 5 | QA 日常 80% 时间都在用 |
| 🟡 强推 | 5 | 完整测试工具链必备 |
| 🟠 按需 | 8 | 特定场景（前端 / 性能 / 移动）才上 |
| ⚫ 不推荐 | 8 | QA 几乎碰不到 |
| **合计** | **26** | tools/ 全部 26 个 MCP |

---

## 🟢 重点必备（5 个）

| MCP | 路径 | QA 视角的核心用法 |
|-----|------|------------------|
| **Browser** | [技术/前端/Browser.md](../技术/前端/Browser.md) | **E2E 测试核心**；Playwright 自动化、截图验证、表单/UI 流程 |
| **E2B** | [技术/测试/E2B.md](../技术/测试/E2B.md) | 跑测试代码、压测脚本、数据构造；隔离沙箱防止污染环境 |
| **Sentry** | [技术/测试/Sentry.md](../技术/测试/Sentry.md) | **线上 Bug 雷达**；复现用户报错、抓现场堆栈 |
| **Sequential Thinking** | [技术/知识库/Sequential-Thinking.md](../技术/知识库/Sequential-Thinking.md) | 复杂 Bug 推理链、测试用例设计、回归策略 |
| **Linear** | [技术/运维/Linear.md](../技术/运维/Linear.md) | **Bug 工单主战场**；建 bug 单、跟踪修复、回归验证 |

---

## 🟡 强推（5 个）

| MCP | 路径 | QA 视角的用法 |
|-----|------|--------------|
| **HTTP Client** | [技术/后端/HTTP-Client.md](../技术/后端/HTTP-Client.md) | API 测试、接口自动化、契约测试；白名单严格配 |
| **Database** | [技术/后端/Database.md](../技术/后端/Database.md) | 验证数据落地、构造测试数据、清理脏数据（只读 + E2B 跑变更） |
| **Filesystem** | [技术/运维/Filesystem.md](../技术/运维/Filesystem.md) | 受限读测试日志、查 fixture、对比截图（**比 Desktop 安全**） |
| **Notion** | [技术/运维/Notion.md](../技术/运维/Notion.md) | 测试用例库、测试报告、QA SOP |
| **Memory** | [技术/知识库/Memory.md](../技术/知识库/Memory.md) | **历史 Bug 知识图谱**；"X 模块易出 Y 类问题"沉淀 |

---

## 🟠 按需（8 个）

### 协作 & 沟通

| MCP | 路径 | 用法 |
|-----|------|------|
| **Slack** | [技术/运维/Slack.md](../技术/运维/Slack.md) | 海外团队 / 客户；测试报告 / 失败告警推送 |
| **钉钉** | [行业/即时通讯/钉钉.md](../行业/即时通讯/钉钉.md) | 国内团队 / 客户；测试告警、@责任人 |
| **GitHub** | [技术/运维/GitHub.md](../技术/运维/GitHub.md) | 看 PR、关联 Bug 修复、Actions 跑测试 |

### 调研 & 文档

| MCP | 路径 | 用法 |
|-----|------|------|
| **Brave Search** | [技术/知识库/Brave-Search.md](../技术/知识库/Brave-Search.md) | 搜测试最佳实践、自动化工具对比、bug 社区 |
| **Docfork** | [技术/知识库/Docfork.md](../技术/知识库/Docfork.md) | 查测试框架文档（Cypress / Playwright / pytest） |
| **Context7** | [技术/知识库/Context7.md](../技术/知识库/Context7.md) | 查测试库精确文档 |

### 杂项

| MCP | 路径 | 用法 |
|-----|------|------|
| **Google Sheets** | [技术/运维/Google-Sheets.md](../技术/运维/Google-Sheets.md) | 测试覆盖率表、回归通过率、QA 指标 |
| **Figma** | [技术/前端/Figma.md](../技术/前端/Figma.md) | UI 测试对比设计稿（自动化视觉回归） |

---

## ⚫ 不推荐（8 个）

| MCP | 路径 | 原因 |
|-----|------|------|
| **Desktop Commander** | [技术/后端/Desktop-Commander.md](../技术/后端/Desktop-Commander.md) | ❌ **高风险**；E2B 跑命令更安全 |
| **Git** | [技术/运维/Git.md](../技术/运维/Git.md) | ❌ 用 GitHub MCP 即可；QA 很少本地 git 操作 |
| **Memory** | 在强推里 | （不是不推荐） |
| **HTTP Client** | 在强推里 | （不是不推荐） |
| **Composio** | [技术/运维/Composio.md](../技术/运维/Composio.md) | ❌ 统一接入平台，QA 维护没价值 |
| **DeepWiki** | [技术/知识库/DeepWiki.md](../技术/知识库/DeepWiki.md) | ❌ 抓 Wiki 是 Tech Writer 的活 |
| **高德地图** | [行业/地图导航/高德地图.md](../行业/地图导航/高德地图.md) | ❌ 跟测试工作无关 |
| **天气** | [行业/天气/天气.md](../行业/天气/天气.md) | ❌ 跟测试工作无关 |

---

## 🔥 实战工作流

### 工作流 1：从用户报错到 Bug 复现

```text
 Sentry 报错       QA 工程师          Browser MCP      Playwright
   │                 │                  │                │
   │  P1 新增       │                  │                │
   ├────────────────▶│                  │                │
   │                 │  get_issue      │                │
   │                 │  拉堆栈 + 设备  │                │
   │                 │                  │                │
   │                 │  Sequential     │                │
   │                 │  Thinking       │                │
   │                 │  拆解复现路径  │                │
   │                 │                  │                │
   │                 │  Browser 打开   │                │
   │                 ├─────────────────▶│                │
   │                 │                  │  启动 Chromium│
   │                 │                  ├───────────────▶│
   │                 │                  │                │
   │                 │  模拟用户操作  │                │
   │                 │  click + fill   │                │
   │                 ├─────────────────▶│                │
   │                 │                  │  执行步骤     │
   │                 │                  ├───────────────▶│
   │                 │                  │                │
   │                 │                  │  复现成功!    │
   │                 │                  │  截图         │
   │                 │                  ├───────────────┤
   │                 │                  │                │
   │                 │  Linear 建 Bug  │                │
   │                 │  ENG-789         │                │
   │                 │  + 截图         │                │
   │                 │  + 复现步骤     │                │
   │                 │  + 堆栈         │                │
   │                 │                  │                │
   │                 │  Notion 测试报告│                │
   │                 │  关联 Bug 单     │                │
   │                 │                  │                │
   │                 │  Memory 沉淀    │                │
   │                 │  "X 页面在 IE Y 版本易崩"           │
```

### 工作流 2：API 自动化测试

```text
 需求文档          QA 工程师          HTTP Client      E2B
 (OpenAPI)              │                  │              │
     │  解析接口        │                  │              │
     ├─────────────────▶│                  │              │
     │                  │                  │              │
     │                  │  Sequential     │              │
     │                  │  Thinking       │              │
     │                  │  设计测试矩阵   │              │
     │                  │                  │              │
     │                  │  1. 正常请求   │              │
     │                  ├─────────────────▶│              │
     │                  │                  │  200 OK     │
     │                  │◀─────────────────┤              │
     │                  │                  │              │
     │                  │  2. 异常请求   │              │
     │                  │  401/404/500   │              │
     │                  ├─────────────────▶│              │
     │                  │                  │              │
     │                  │  3. 边界值    │              │
     │                  │                  │              │
     │                  │  4. 性能压测  │              │
     │                  ├───────────────────────────────────▶│
     │                  │                  │  跑 100 并发 │
     │                  │                  │              │
     │                  │  5. 数据落地验证                  │
     │                  │  Database 查 DB │              │
     │                  ├─────────────────▶│              │
     │                  │                  │              │
     │                  │  生成 HTML 报告 │              │
     │                  ├───────────────────────────────────▶│
     │                  │                  │              │
     │                  │  失败告警       │              │
     │                  │  钉钉           │              │
     │                  │                  │              │
     │                  │  Linear 失败单  │              │
```

### 工作流 3：回归测试流水线

```text
 PR 合并           GitHub Actions       QA Bot         Browser
   │                    │                │                │
   │  merge main        │                │                │
   ├───────────────────▶│                │                │
   │                    │  trigger       │                │
   │                    │  regression job │                │
   │                    │                │                │
   │                    │  1. unit test │                │
   │                    │  2. e2e test  │                │
   │                    ├───────────────▶│                │
   │                    │                │  跑 Playwright│
   │                    │                ├───────────────▶│
   │                    │                │                │
   │                    │                │  截图对比     │
   │                    │                │  vs baseline │
   │                    │                │                │
   │                    │                │  报告         │
   │                    │                │  - 23 passed │
   │                    │                │  - 1 failed  │
   │                    │                │                │
   │                    │                │  Linear 自动 │
   │                    │                │  建 bug 单    │
   │                    │                │                │
   │                    │                │  Slack 通知   │
   │                    │                │  失败详情     │
```

---

## 💡 实战建议

1. **Browser 是 E2E 的"瑞士军刀"** — 表单、截图、JS 注入一站式
2. **E2B 跑测试代码** — 别在 CI runner 上跑裸命令，隔离更安全
3. **Sentry + Browser 是 Bug 复现黄金组合** — Sentry 给数据，Browser 给复现路径
4. **Sequential Thinking 用在复杂 Bug** — 别直接套命令，推理优先
5. **Linear 是 Bug 唯一来源** — 别再用 Excel / 邮件跟踪 Bug
6. **HTTP Client 做接口测试** — 比 Postman 强，因为能跟其他 MCP 串联
7. **Database 只读账号** — QA 也别拿 root 连生产；构造数据用 E2B
8. **Filesystem 替代 Desktop Commander** — 读测试 fixture 更安全
9. **Memory 沉淀"历史 Bug"** — 同一个坑不要踩两次
10. **永远不碰 Desktop Commander** — 权限太大，QA 用不到

---

## 🔗 相关工具

- [FDE 装备清单](./FDE.md) — 现场部署视角
- [PM 装备清单](./PM.md) — 产品视角
- [SRE 装备清单](./SRE.md) — 运维视角
- [Data Engineer 装备清单](./Data-Engineer.md) — 数据视角
- [Tech Lead 装备清单](./Tech-Lead.md) — 技术管理视角
- [回到 README 索引](../README.md)
- [总 .env 配置模板](../.env.example)
