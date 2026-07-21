# ⚛️ ReactBits MCP

> 分类：技术 / 前端
> 项目主页：<https://reactbits.dev/>
> 适用场景：动画 React 组件源码、UI 动效参考、组件搜索

---

## 一、简介

ReactBits 收录了 135+ 高质量、带动画效果的 React 组件源码，涵盖按钮、卡片、文本动画、加载器、背景效果等。每个组件都附带：
- 演示视频
- 完整源码（Tailwind / CSS 两种）
- 一键复制

ReactBits MCP 让 LLM 能在对话中**直接搜索、引用、生成**这些组件源码。

> 默认工具数：5

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 组件搜索 | 关键字 / 分类 / 标签 |
| 获取源码 | Tailwind 版 / CSS 版 / JSX 全文 |
| 查看演示 | 演示视频链接 + 动效描述 |
| 推荐组合 | 基于场景推荐组件组合 |
| 导入方式 | npm 包名 / CDN / GitHub 路径 |

---

## 三、配置

### 3.1 环境变量

```bash
# 可选：GitHub Token（提升 API 限流）
# Personal Access Token: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx

# 可选：默认样式风格
REACTBITS_DEFAULT_STYLE=tailwind    # tailwind | css

# 可选：是否包含 TypeScript 版本
REACTBITS_INCLUDE_TYPESCRIPT=true
```

> 没有 GitHub Token 也能用，但可能撞到 GitHub API 限流（未认证 60 次/小时，认证 5000 次/小时）。

### 3.2 数据来源

ReactBits 组件源码托管在 GitHub：<https://github.com/DavidHDev/react-bits>

MCP 通过抓取 GitHub 仓库 + 自维护索引来提供组件查询能力。

---

## 四、使用示例

### 4.1 搜索组件

```bash
curl -X POST http://localhost:8000/mcp/execute/reactbits/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "loading spinner",
    "category": "loaders"
  }'
```

返回：

```json
{
  "results": [
    {
      "name": "PulseLoader",
      "category": "loaders",
      "tags": ["pulse", "minimal", "react"],
      "demo_url": "https://reactbits.dev/loaders/pulse-loader",
      "source_url": "https://github.com/DavidHDev/react-bits/blob/main/src/components/loaders/PulseLoader.jsx"
    }
  ]
}
```

### 4.2 获取组件源码

```bash
curl -X POST http://localhost:8000/mcp/execute/reactbits/get_source \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "component": "PulseLoader",
    "style": "tailwind",
    "typescript": true
  }'
```

返回完整 JSX/TSX 源码。

### 4.3 按分类列出

```bash
curl -X POST http://localhost:8000/mcp/execute/reactbits/list_by_category \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "text-animations",
    "limit": 20
  }'
```

分类参考：
- `buttons`
- `cards`
- `loaders`
- `text-animations`
- `backgrounds`
- `navigation`
- `inputs`
- `modals`

---

## 五、典型使用流程

### 场景：用户问"做一个加载动画"

```text
 用户              LLM            ReactBits MCP        GitHub
  │                 │                  │                │
  │ "做一个加载动画" │                  │                │
  ├────────────────▶│                  │                │
  │                 │  search "loader" │                │
  │                 ├─────────────────▶│                │
  │                 │                  │  GitHub 搜索   │
  │                 │                  ├───────────────▶│
  │                 │                  │◀───────────────┤
  │                 │  [PulseLoader,   │                │
  │                 │   Spinner, ...]  │                │
  │                 │◀─────────────────┤                │
  │                 │  推荐 PulseLoader                │
  │                 │  (最小、最快)    │                │
  │                 │  get_source     │                │
  │                 ├─────────────────▶│                │
  │                 │                  │  拉源码       │
  │                 │                  ├───────────────▶│
  │                 │                  │◀───────────────┤
  │                 │  Tailwind 版 TSX│                │
  │                 │◀─────────────────┤                │
  │                 │                  │                │
  │                 │ Filesystem 写到项目                │
  │                 ├─────────────────┐│                │
  │                 │                 ▼│                │
  │                 │  src/components/PulseLoader.tsx   │
  │                 │                  │                │
  │                 │  import + 使用   │                │
  │ "搞定"           │                  │                │
  │◀────────────────┤                  │                │
```

### 场景：基于设计稿找匹配的动效组件

```text
 Figma 设计稿      Figma MCP        LLM          ReactBits MCP
     │                │              │                │
     │ get_layout    │              │                │
     ├──────────────▶│              │                │
     │  颜色 / 风格  │              │                │
     │◀──────────────┤              │                │
     │                │  "极简风格  │                │
     │                │   蓝白主色"  │                │
     │                ├─────────────▶│                │
     │                │              │  search       │
     │                │              │ "minimal blue"│
     │                │              ├───────────────▶│
     │                │              │  [AnimatedCard,
     │                │              │   FadeIn,...]  │
     │                │              │◀───────────────┤
     │                │  推荐 AnimatedCard                │
     │                │  配色 + 风格匹配                  │
     │                │◀─────────────┤                │
```

LLM 在这里主要做"选型 + 适配"：从 135 个组件里挑最合适的，整理出符合项目代码风格的版本。

---

## 六、注意事项

- **样式版本**：优先选 Tailwind 版（与项目风格一致），CSS 版适合无 Tailwind 的项目
- **依赖**：部分组件依赖 `framer-motion`，需要先安装
- **TypeScript**：默认 true，源码带类型；如果项目是 JS 设成 false
- **版权**：MIT License，可以商用，但建议保留原作者署名
- **演示视频**：仅展示效果，**不能直接 copy 视频到项目**

---

## 七、相关工具

- [Figma](./Figma.md) - 拿到设计稿后用 ReactBits 拼组件
- [Browser](./Browser.md) - 截图验证动效实现效果
- [Context7](../知识库/Context7.md) - 查 framer-motion 等依赖的精确文档
