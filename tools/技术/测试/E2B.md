# 📦 E2B MCP（云端代码沙箱）

> 分类：技术 / 测试（也常用于数据分析 / 实验）
> 官网：<https://e2b.dev/>
> 适用场景：安全执行任意代码、数据分析、爬虫实验、临时测试

---

## 一、简介

E2B 提供**云端隔离沙箱**，让 LLM 可以安全地执行任意 Python / JavaScript 代码：
- 沙箱每次启动一个全新环境（Ubuntu + Python/Node）
- 默认 24 小时后自动销毁
- 沙箱之间完全隔离
- 支持安装任意包（pip / npm）

适用：数据处理、爬虫脚本、代码片段验证、SQL 跑批、临时绘图等。

> 默认工具数：7

---

## 二、核心能力

| 能力 | 说明 |
|------|------|
| 创建沙箱 | 启动一个全新隔离环境 |
| 执行 Python | 任意 Python 代码 |
| 执行 JS | Node.js 任意代码 |
| 上传文件 | 把本地文件传到沙箱 |
| 下载文件 | 把沙箱里的文件拉回来 |
| 装包 | pip / npm install |
| 持久化 | 沙箱内数据保留（生命周期内） |

---

## 快速配置

> 直接复制以下片段到 `.env`，再补全你的 Key。完整模板见 [`.env.example`](.env.example)。
>
> 图例：`[REQUIRED]` 必填 · `[STRONG]` 强烈建议 · 其他可选

### 必填

```bash
E2B_API_KEY=e2b_xxxxxxxxxxxxxxxx  # API Key
```

### 可选

```bash
E2B_DEFAULT_TEMPLATE=base  # 默认模板
E2B_DEFAULT_TIMEOUT=300  # 秒
E2B_MAX_LIFETIME=86400  # 沙箱最大存活秒
```

---

## 三、配置

### 3.1 申请 API Key

1. 打开 <https://e2b.dev/>
2. 注册 → Dashboard → 复制 API Key

### 3.2 环境变量

```bash
# 必填
E2B_API_KEY=e2b_xxxxxxxxxxxxxxxx

# 可选：默认模板（Ubuntu 22.04 / Python 3.11）
E2B_DEFAULT_TEMPLATE=base

# 可选：默认超时（秒）
E2B_DEFAULT_TIMEOUT=300

# 可选：沙箱最大存活时间（秒）
E2B_MAX_LIFETIME=86400              # 24 小时
```

---

## 四、使用示例

### 4.1 执行 Python

```bash
curl -X POST http://localhost:8000/mcp/execute/e2b/execute_code \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import numpy as np\nprint(np.mean([1,2,3,4,5]))",
    "language": "python"
  }'
```

返回：

```json
{
  "stdout": "3.0\n",
  "stderr": "",
  "exit_code": 0,
  "duration_ms": 234
}
```

### 4.2 复杂数据处理

```bash
curl -X POST http://localhost:8000/mcp/execute/e2b/execute_code \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndf = pd.read_csv(\"/tmp/data.csv\")\ndf.groupby(\"category\")[\"amount\"].sum().plot(kind=\"bar\")\nplt.savefig(\"/tmp/chart.png\")\nprint(\"chart saved\")\n",
    "language": "python"
  }'
```

### 4.3 装包 + 跑脚本

```bash
# 第一步：装包
curl -X POST http://localhost:8000/mcp/execute/e2b/install_package \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "package": "requests beautifulsoup4",
    "manager": "pip"
  }'

# 第二步：跑爬虫
curl -X POST http://localhost:8000/mcp/execute/e2b/execute_code \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import requests; from bs4 import BeautifulSoup\nr = requests.get(\"https://example.com\")\nprint(BeautifulSoup(r.text, \"html.parser\").title.string)"
  }'
```

### 4.4 上传 / 下载文件

```bash
# 上传
curl -X POST http://localhost:8000/mcp/execute/e2b/upload_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sandbox_id": "sb_xxx",
    "local_path": "./data.csv",
    "remote_path": "/tmp/data.csv"
  }'

# 下载
curl -X POST http://localhost:8000/mcp/execute/e2b/download_file \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sandbox_id": "sb_xxx",
    "remote_path": "/tmp/chart.png",
    "local_path": "./chart.png"
  }'
```

---

## 五、典型使用流程

### 场景：用户上传 CSV，LLM 帮你分析

```text
  用户             LLM            E2B MCP            E2B 云端沙箱
   │                │                 │                    │
   │  上传 CSV     │                 │                    │
   ├───────────────▶│                 │                    │
   │                │  upload_file    │                    │
   │                ├────────────────▶│                    │
   │                │                 │  POST /files       │
   │                │                 ├───────────────────▶│
   │                │                 │  /tmp/data.csv     │
   │                │                 │◀───────────────────┤
   │                │                 │                    │
   │                │  execute_code   │                    │
   │                │  pandas + matplotlib                    │
   │                ├────────────────▶│                    │
   │                │                 │  启动 Python       │
   │                │                 │  + 装包            │
   │                │                 ├───────────────────▶│
   │                │                 │                    │
   │                │                 │  执行脚本          │
   │                │                 │  stdout + 图表     │
   │                │                 │◀───────────────────┤
   │                │  stdout: "chart saved"                 │
   │                │  chart.png 路径                        │
   │                │◀────────────────┤                    │
   │                │                                    │
   │                │  download_file                       │
   │                ├────────────────▶│                    │
   │                │                 │  GET /files        │
   │                │                 ├───────────────────▶│
   │                │                 │◀───────────────────┤
   │                │  本地 chart.png│                    │
   │                │                 │                    │
   │ "图表 + 分析"  │                 │                    │
   │◀───────────────┤                 │                    │
```

### 场景：LLM 自测代码

```text
 LLM            E2B MCP            E2B 沙箱
  │                 │                  │
  │  LLM 写代码后   │                  │
  │  想先验证       │                  │
  │                 │                  │
  │  execute_code   │                  │
  │  test code      │                  │
  ├────────────────▶│                  │
  │                 │  运行 test        │
  │                 ├─────────────────▶│
  │                 │  5 passed        │
  │                 │  0 failed        │
  │                 │◀─────────────────┤
  │  ✅ 自测通过    │                  │
  │◀────────────────┤                  │
  │                 │                  │
  │  把代码 commit  │                  │
  │  到仓库         │                  │
```

### 场景：数据爬虫（安全执行）

```text
 用户             LLM            E2B 沙箱
  │                │                  │
  │ "爬取某网站    │                  │
  │  商品价格"     │                  │
  ├───────────────▶│                  │
  │                │  install requests│
  │                │  + bs4           │
  │                ├─────────────────▶│
  │                │                  │
  │                │  execute_code    │
  │                │  requests.get +  │
  │                │  BeautifulSoup   │
  │                ├─────────────────▶│
  │                │                  │
  │                │  隔离环境跑     │
  │                │  即使代码有恶意  │
  │                │  也不影响主机   │
  │                │                  │
  │                │  stdout + 文件  │
  │                │◀────────────────┤
  │  价格表 + 趋势图                  │
  │◀───────────────┤                  │
```

适合：
- 数据分析
- 临时跑数据脚本（避免污染本地）
- LLM 自测代码
- 教学演示

---

## 六、对比其他代码执行方案

| 方案 | 隔离性 | 速度 | 费用 |
|------|:------:|:----:|------|
| **E2B** | ⭐⭐⭐⭐⭐ | 启动 1~3s | 免费额度 + 按秒计费 |
| Docker 本地 | ⭐⭐⭐⭐ | 启动 5~10s | 0（自己机器） |
| subprocess 本地 | ⭐ | 启动 < 1s | 0（但风险大） |
| Jupyter Kernel | ⭐⭐ | 启动 1s | 0 |

E2B **隔离性最强 + 0 维护**，适合不可信代码；本地执行**最便宜**，适合自己跑。

---

## 七、注意事项

- **不要把生产密钥放沙箱里** —— 沙箱环境对 E2B 自己可读
- **网络限制**：沙箱默认有外网，但企业内网不通
- **资源限制**：CPU / 内存 / 磁盘有上限，看套餐
- **超时**：单次执行超时会被 kill
- **持久化**：沙箱销毁后所有数据丢失；重要数据要下载
- **可重入**：同一个 `sandbox_id` 可以多次执行（保持状态）

---

## 八、相关工具

- [Database](../后端/Database.md) - 也可以用 SQL 做数据分析
- [Browser](../前端/Browser.md) - JS 渲染抓取
- [Sequential Thinking](../知识库/Sequential-Thinking.md) - 多步分析任务编排

<!-- BACKLINKS START -->

## 🔗 被以下 MCP 引用

> 反向链接自动生成（`scripts/build_backlinks.py`）。

- [Browser](技术/前端/Browser.md)
- [Database](技术/后端/Database.md)
- [Filesystem](技术/运维/Filesystem.md)
- [Google-Sheets](技术/运维/Google-Sheets.md)

<!-- BACKLINKS END -->
