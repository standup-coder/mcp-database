# 🌐 Browser MCP（Playwright）

> 分类：技术 / 前端（也常用于测试）
> 底层：Playwright（支持 Chromium / Firefox / WebKit）
> 适用场景：浏览器自动化、截图、爬虫、表单填写、E2E 测试

---

## 一、简介

Browser MCP 把 Playwright 包装成 LLM 可调用的工具。LLM 可以驱动真实浏览器：
- 打开任意网页
- 截图（整页 / 视口 / 元素）
- 点击 / 输入 / 滚动
- 执行 JS
- 抓取 DOM 内容
- 模拟移动端

适用：UI 验证、爬虫、E2E 测试、动态页面渲染截图。

> 默认工具数：9

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 打开网页 | URL → 浏览器 |
| 截图 | 整页 / 视口 / 元素，支持 PNG/JPEG/PDF |
| 点击 | 按文字 / 选择器 / 坐标 |
| 输入 | 文本框 / 下拉 / 文件上传 |
| 等待 | 元素 / 网络 / 固定时长 |
| 执行 JS | `page.evaluate` 跑任意 JS |
| 提取 DOM | HTML / 文本 / 属性 |
| 移动端模拟 | iPhone / iPad / Pixel |
| 多标签页 | 标签页上下文管理 |

---

## 三、配置

### 3.1 安装依赖

```bash
# 安装 Playwright 浏览器
pip install playwright
playwright install chromium
# 也可装全部
playwright install
```

### 3.2 环境变量

```bash
# 可选：默认浏览器
BROWSER_DEFAULT_ENGINE=chromium       # chromium | firefox | webkit

# 可选：是否无头模式
BROWSER_HEADLESS=true                # 生产环境必须 true

# 可选：超时（毫秒）
BROWSER_DEFAULT_TIMEOUT=30000

# 可选：默认视口
BROWSER_VIEWPORT_WIDTH=1920
BROWSER_VIEWPORT_HEIGHT=1080

# 可选：截图目录
BROWSER_SCREENSHOT_DIR=./downloads/screenshots

# 可选：代理（企业内网必备）
# BROWSER_PROXY=http://proxy.company.com:8080

# 可选：User-Agent
# BROWSER_USER_AGENT=Mozilla/5.0 ...
```

### 3.3 反爬注意

- 默认 **headless**，但有些网站会检测 `navigator.webdriver`
- 必要时设 `BROWSER_USER_AGENT` 伪装真实浏览器
- 高频访问会被封 IP，建议加随机 `sleep` + 代理池

---

## 四、使用示例

### 4.1 截图整页

```bash
curl -X POST http://localhost:8000/mcp/execute/browser/screenshot \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "full_page": true,
    "format": "png"
  }'
```

### 4.2 点击 + 输入

```bash
curl -X POST http://localhost:8000/mcp/execute/browser/click \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/login",
    "selector": "input[name=username]",
    "value": "alice"
  }'
```

### 4.3 执行 JS 抓数据

```bash
curl -X POST http://localhost:8000/mcp/execute/browser/evaluate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.ycombinator.com",
    "script": "Array.from(document.querySelectorAll(\".titleline > a\")).map(a => a.textContent)"
  }'
```

### 4.4 移动端截图

```bash
curl -X POST http://localhost:8000/mcp/execute/browser/screenshot \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://m.example.com",
    "device": "iPhone 15 Pro",
    "full_page": true
  }'
```

### 4.5 生成 PDF

```bash
curl -X POST http://localhost:8000/mcp/execute/browser/pdf \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article/123",
    "format": "A4"
  }'
```

---

## 五、典型使用流程

### 场景：UI 验证 — 截图对比实现效果

```text
 设计稿          Figma MCP       浏览器 MCP         截图
 (Figma)            │               │                │
    │  get_layout  │               │                │
    ├─────────────▶│               │                │
    │  期望样式    │               │                │
    │◀─────────────┤               │                │
    │               │  打开本地     │                │
    │               │  localhost:3000                │
    │               ├──────────────▶│                │
    │               │               │  Playwright    │
    │               │               │  启动 Chromium │
    │               │               │  全页截图      │
    │               │               ├───────────────▶│
    │               │               │                │
    │               │  像素级对比   │                │
    │               │  期望 vs 实际  │                │
    │               │               │  差异 0.3%    │
    │               │◀──────────────┤                │
    │               │  ✅ 基本一致                  │
```

### 场景：动态页面爬虫（需要 JS 渲染）

```text
 目标 URL        Browser MCP         Playwright          解析
 (SPA 网站)         │                  │                │
     │  evaluate   │                  │                │
     ├────────────▶│                  │                │
     │  JS 脚本    │                  │                │
     │             │  注入 JS        │                │
     │             ├─────────────────▶│                │
     │             │                  │  执行          │
     │             │                  │  等待 DOM      │
     │             │                  │  + 抓数据     │
     │             │                  ├───────────────▶│
     │             │                  │                │
     │             │  提取结果       │                │
     │             │◀─────────────────┤                │
     │  [{},{},..] │                  │                │
     │◀────────────┤                  │                │
     │
     ▼
   写入 E2B 沙箱做进一步分析
```

---

## 六、与 E2E 测试的关系

| 场景 | 推荐工具 |
|------|---------|
| **生产环境数据抓取 / 截图** | 本 Browser MCP |
| **CI 自动化 E2E** | Playwright / Cypress 测试框架 |
| **长期爬虫** | Scrapy / Puppeteer（更专业） |

> Browser MCP 偏向"一次性 / 偶发"任务；持续集成测试建议用专用框架。

---

## 六、注意事项

- **资源占用**：每个浏览器实例占 200~500MB 内存，并发要控制
- **超时**：复杂页面 `BROWSER_DEFAULT_TIMEOUT` 建议设到 60000+
- **反爬**：高频访问会被识别为机器人，建议加 `sleep(1~3)`
- **登录态**：Cookie 不会跨实例保留，长任务建议持久化 Cookie
- **安全**：**不要**用这个爬取敏感数据（密码、个人信息）

---

## 七、相关工具

- [E2B](../测试/E2B.md) - 把抓到的数据丢到 E2B 沙箱里分析
- [Figma](./Figma.md) - 设计稿 vs 实现的视觉对比
- [Sentry](../测试/Sentry.md) - 抓取生产页面报错截图
