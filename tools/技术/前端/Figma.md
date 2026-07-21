# 🎨 Figma MCP

> 分类：技术 / 前端
> 提供方：Figma
> 适用场景：设计稿数据获取、布局解析、图片资源下载、设计转代码

---

## 一、简介

Figma MCP 把 Figma 设计文件暴露给 LLM。LLM 可以读取节点的布局、样式、文本内容、组件结构，也可以下载图片资源。
典型场景：把 Figma 设计稿转成 React / Vue 组件、把设计资源批量下载到项目。

> 默认工具数：2

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 读取设计稿 | 获取节点的层级、坐标、尺寸、样式 |
| 提取文本 | 一键导出设计稿里所有文案 |
| 解析组件 | Component 树 + 变体（Variants）信息 |
| 下载图片 | 导出 PNG / SVG / JPG 到本地 |
| 设计 Token | 颜色、字体、间距等设计变量 |

---

## 三、配置

### 3.1 申请 Personal Access Token

1. 登录 Figma → 头像 → Settings
2. 左侧 "Account" → 滚到 "Personal access tokens"
3. 点击 "Generate new token"
4. 命名 + 设置过期时间 + 勾选需要的 scope（至少 `File reads`）
5. 复制 Token（**只显示一次**）

### 3.2 环境变量

```bash
# 必填
FIGMA_API_KEY=figd_xxxxxxxxxxxxxxxx

# 可选：默认导出格式
FIGMA_EXPORT_FORMAT=png            # png | svg | jpg | pdf

# 可选：默认导出尺寸缩放
FIGMA_EXPORT_SCALE=2               # 1 | 2 | 3 | 4

# 可选：下载目录
FIGMA_DOWNLOAD_DIR=./downloads/figma
```

### 3.3 从 URL 提取 File Key

Figma URL 格式：
```
https://www.figma.com/file/<FILE_KEY>/<FILE_NAME>?node-id=<NODE_ID>
```

例如：
```
https://www.figma.com/file/aBcD1234/MyDesign?node-id=12-34
                          ^^^^^^^^                              ^^^^
                          File Key                              Node ID
```

Node ID 中的 `-` 在 API 里要变成 `%2D`（框架自动处理）。

---

## 四、使用示例

### 4.1 读取设计稿布局

```bash
curl -X POST http://localhost:8000/mcp/execute/figma/get_layout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_key": "aBcD1234",
    "node_id": "12-34"
  }'
```

返回（简化）：

```json
{
  "name": "LoginPage",
  "type": "FRAME",
  "x": 0, "y": 0, "width": 1440, "height": 900,
  "children": [
    {
      "name": "Title",
      "type": "TEXT",
      "characters": "欢迎登录",
      "style": { "fontSize": 32, "fontWeight": 700, "color": "#1A1A1A" }
    }
  ]
}
```

### 4.2 提取所有文本

```bash
curl -X POST http://localhost:8000/mcp/execute/figma/extract_text \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_key": "aBcD1234",
    "node_id": "12-34"
  }'
```

返回文案数组，方便做 i18n 词条抽取。

### 4.3 下载图片资源

```bash
curl -X POST http://localhost:8000/mcp/execute/figma/export_image \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_key": "aBcD1234",
    "node_id": "56-78",
    "format": "svg",
    "scale": 2
  }'
```

下载的文件默认保存到 `FIGMA_DOWNLOAD_DIR`。

### 4.4 获取设计变量（Design Tokens）

```bash
curl -X POST http://localhost:8000/mcp/execute/figma/get_variables \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"file_key": "aBcD1234"}'
```

---

## 五、典型使用流程

### 场景：Figma 设计稿 → React 组件

```text
  Figma 文件           Figma MCP             LLM                项目
   (设计稿)               │                  │                  │
      │   get_layout     │                  │                  │
      ├─────────────────▶│                  │                  │
      │  节点 + 样式      │                  │                  │
      │◀─────────────────┤                  │                  │
      │                  │  解析 JSON       │                  │
      │                  ├─────────────────▶│                  │
      │                  │                  │  生成 React 组件 │
      │                  │                  │  + Tailwind 样式 │
      │                  │                  │  + TypeScript    │
      │                  │                  ├─────────────────▶│
      │                  │                  │  src/Login.tsx   │
      │   extract_text   │                  │                  │
      ├─────────────────▶│                  │                  │
      │  文案数组        │                  │                  │
      │◀─────────────────┤                  │                  │
      │                  │                  │  生成 i18n 文件 │
      │                  │                  ├─────────────────▶│
      │                  │                  │  zh-CN.json      │
      │                  │                  │  en-US.json      │
      │   export_image   │                  │                  │
      ├─────────────────▶│                  │                  │
      │  PNG / SVG       │                  │                  │
      │◀─────────────────┤                  │                  │
      │                  │                  │  下载到 assets/ │
      │                  │                  ├─────────────────▶│
      │                  │                  │  logo.png        │
      │                  │                  │  icon.svg        │
      │                  │                  │
      │                  │                  ▼
      │                  │            浏览器截图对比
      │                  │          （用 Browser MCP）
```

### 场景：批量提取设计 Token 到代码

```text
 Figma 文件        Figma MCP           LLM            项目代码
     │                │                │                 │
     │ get_variables │                │                 │
     ├──────────────▶│                │                 │
     │  colors/space │                │                 │
     │  typography   │                │                 │
     │◀──────────────┤                │                 │
     │                │  解析 tokens  │                 │
     │                ├───────────────▶│                 │
     │                │                │ 生成 design-tokens.ts
     │                │                ├────────────────▶│
     │                │                │  export const colors = {
     │                │                │    primary: '#1A1A1A',
     │                │                │    ...
     │                │                │  }
     │                │                │
     │                │                │ 生成 tailwind.config.ts
     │                │                ├────────────────▶│
     │                │                │  theme: {
     │                │                │    colors: {...}
     │                │                │  }
```

---

## 六、Figma 转代码工作流

```text
设计稿（Figma）
    ↓ get_layout
结构 + 样式 JSON
    ↓ LLM 解析
React / Vue 组件代码
    ↓ export_image
图标 / 图片资源
    ↓
最终页面
```

LLM 在这一步最有价值：它能"看懂"设计稿的语义，把绝对定位转成 Flex 布局，把硬编码颜色换成 Design Token。

---

## 六、注意事项

- **Token 权限**：Personal Token 只能访问你能打开的文件；企业文件需要用 OAuth
- **文件访问**：Figma 文件必须设置"Anyone with the link can view"或你是协作者
- **大文件**：单文件超过 500 节点建议分批拉取，否则响应慢
- **样式精度**：Figma 颜色是 0~1 浮点（`{r: 0.1, g: 0.2, b: 0.3}`），要转成 hex 还需要框架处理
- **版本控制**：Figma 文件本身有版本历史，但通过 API 只能读当前版本

---

## 七、相关工具

- [ReactBits](./ReactBits.md) - 135+ 动画 React 组件，可结合 Figma 配色
- [Browser](./Browser.md) - 截图工具，验证设计稿实现效果
- [Notion](../运维/Notion.md) - 把设计 Token 文档化到 Notion
