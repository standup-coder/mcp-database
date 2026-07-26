# MCP Tool Suite

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Servers](https://img.shields.io/badge/MCP%20Servers-37-orange.svg)](#mcp-服务器一览)
[![Build](https://img.shields.io/github/actions/workflow/status/standup-coder/mcp4coder/ci.yml?branch=main)](https://github.com/standup-coder/mcp4coder/actions)

**37 个 MCP Server，一套统一框架。** 覆盖开发工具链、云平台管理、文档查询、浏览器自动化、设计协作、项目管理、错误监控、代码沙箱、支付通信等场景，配套 Web 管理界面和可视化工作流设计器。

---

## 目录

- [MCP 服务器一览](#mcp-服务器一览)
- [架构概览](#架构概览)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [API 使用](#api-使用)
- [Docker 部署](#docker-部署)
- [安全特性](#安全特性)
- [项目结构](#项目结构)
- [开发新 Server](#开发新-server)
- [Dumb 模式（极简版）](#dumb-模式极简版)
- [2026 MCP 生态趋势](#2026-mcp-生态趋势)
- [Roadmap](#roadmap)
- [文档](#文档)
- [贡献](#贡献)

---

## MCP 服务器一览

### 开发工具链

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 📁 **Filesystem** | 文件读写、目录操作、路径搜索 | 7 | — |
| 🔧 **Git** | 版本控制全操作（commit/branch/diff/log） | 9 | — |
| 🗄️ **Database** | MySQL / PostgreSQL / SQLite / Redis | 7 | — |
| 🌐 **HTTP Client** | 发送任意 HTTP 请求 | 5 | — |
| 📦 **GitHub** | 仓库、Issue、PR、代码搜索 | 10 | `GITHUB_TOKEN` |
| 🖥️ **Desktop Commander** | 终端命令执行、进程管理、文件编辑搜索 | 12 | — |

### 文档与知识

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 📚 **Context7** | 版本精确的库文档实时注入 | 2 | `CONTEXT7_API_KEY`（可选） |
| 📖 **Docfork** | 9000+ 库文档语义搜索 | 2 | `DOCFORK_API_KEY` |
| 📄 **DeepWiki** | DeepWiki 文档 → 结构化 Markdown | 1 | — |
| 🧠 **Memory** | 持久化记忆、知识图谱 | 9 | — |

### 搜索与浏览器

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 🔍 **Brave Search** | 网页、新闻、图片、视频搜索 | 4 | `BRAVE_API_KEY` |
| 🌐 **Browser** | Playwright 浏览器自动化、截图、表单 | 9 | — |

### 团队协作与项目管理

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 💬 **Slack** | 消息推送、频道管理 | 8 | `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` |
| 📝 **Notion** | 页面、数据库、Block 管理 | 7 | `NOTION_TOKEN` |
| 📊 **Google Sheets** | 表格创建、读写、格式化 | 6 | `GOOGLE_CREDENTIALS_PATH` |
| 📋 **Linear** | Issue CRUD、搜索、评论 | 5 | `LINEAR_API_KEY` |
| 🔗 **Composio** | 500+ 应用统一集成（Slack/Jira/Gmail…） | 6 | `COMPOSIO_API_KEY` |

### 设计与前端

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 🎨 **Figma** | 设计稿布局获取、图片资源下载 | 2 | `FIGMA_API_KEY` |
| ⚛️ **ReactBits** | 135+ 动画 React 组件源码库 | 5 | `GITHUB_TOKEN`（可选） |

### 代码执行与监控

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 📦 **E2B** | 云端安全代码沙箱（Python/JS） | 7 | `E2B_API_KEY` |
| 🐛 **Sentry** | 错误监控、Issue 跟踪、事件分析 | 8 | `SENTRY_ACCESS_TOKEN` |

### AI 推理

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 🧩 **Sequential Thinking** | 结构化推理、思维链分支与修订 | 1 | — |

### 生活与效率

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 🗺️ **高德地图** | 路线规划、地理编码、实时路况 | 4 | `AMAP_API_KEY` |
| 💬 **钉钉** | Webhook 消息推送、群通知 | 3 | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` |
| 🌤️ **天气** | 实时天气、多日预报 | 3 | — |
| 📅 **日历** | 日程管理、提醒 | 3 | — |

> **合计：37 个 Server，200+ Tools**

### 云平台与基础设施

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| ☁️ **Cloudflare** | Workers 部署、D1 数据库、KV 存储、R2 对象存储、DNS 管理 | 10 | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` |
| 🔺 **Vercel** | 项目部署、域名管理、环境变量、部署日志 | 8 | `VERCEL_TOKEN` |
| 🟢 **Supabase** | PostgreSQL 数据库、Auth 用户管理、Storage、Edge Functions | 9 | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |
| 🟠 **AWS** | S3 存储桶、Lambda 函数、EC2 实例、CloudWatch 日志 | 12 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |

### 企业协作与项目管理

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 🎯 **Jira** | Issue 创建/更新、Sprint 管理、看板查询 | 8 | `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| 📘 **Confluence** | 页面创建/读取、空间搜索、内容更新 | 6 | `CONFLUENCE_URL`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN` |

### 支付与通信

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 💳 **Stripe** | 支付意图、客户管理、订阅、退款操作 | 9 | `STRIPE_SECRET_KEY` |
| 📱 **Twilio** | SMS/MMS 发送、语音通话、WhatsApp 消息 | 6 | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` |

### 地图与可观测性

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 🗺️ **Google Maps** | 地点搜索、路线规划、地理编码、附近搜索 | 7 | `GOOGLE_MAPS_API_KEY` |
| 📊 **Datadog** | 指标查询、日志搜索、告警管理、事件追踪 | 8 | `DATADOG_API_KEY`, `DATADOG_APP_KEY` |

### API 与规范

| Server | 说明 | Tools | 所需环境变量 |
|--------|------|:-----:|-------------|
| 📐 **OpenAPI** | OpenAPI/Swagger 规范解析、接口文档查询、Mock 数据生成 | 5 | — |

---

## 架构概览

```
                    ┌───────────────┐
                    │  Web UI /ui   │
                    │  Swagger /docs│
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │   FastAPI     │
                    │   REST API    │
                    │  Auth + CORS  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
     ┌────────▼──────┐ ┌───▼───┐ ┌──────▼──────┐
     │ ServerFactory │ │Service│ │  Celery     │
     │ 26 Servers    │ │ Layer │ │  Workers    │
     └────────┬──────┘ └───────┘ └──────┬──────┘
              │                         │
     ┌────────▼──────┐          ┌──────▼──────┐
     │ BaseMCPServer │          │    Redis    │
     │ register_tools│          │  Broker +   │
     │ execute_tool  │          │  Result     │
     └───────────────┘          └─────────────┘
```

**核心模式：** 所有 Server 继承 `BaseMCPServer`，实现 `register_tools` → `execute_tool` 的统一接口。`ServerFactory` 管理 Server 配置和生命周期，`MCPServerManager` 负责进程监控和健康检查。

---

## 快速开始

### 1. 安装

```bash
git clone https://github.com/standup-coder/mcp4coder.git
cd mcp4coder

# 安装项目（含开发依赖）
pip install -e ".[dev]"

# 可选：安装特定 Server 的依赖
pip install -e ".[browser]"     # 浏览器自动化
pip install -e ".[google]"      # Google Sheets
pip install -e ".[notion]"      # Notion
pip install -e ".[database]"    # 数据库驱动
pip install -e ".[all]"         # 全部可选依赖
```

### 2. 配置环境变量

```bash
cp config/.env.example .env
# 编辑 .env 填入你的 API Key
```

> 必填项：`AMAP_API_KEY`、`AMAP_ORIGIN`、`AMAP_DESTINATION`、`DINGTALK_WEBHOOK_URL`、`DINGTALK_SECRET`、`CELERY_BROKER_URL`、`CELERY_RESULT_BACKEND`
>
> 生产环境必填：`JWT_SECRET_KEY`（未设置将拒绝启动）

### 3. 启动

```bash
# 启动 Redis（如果用 Docker）
docker compose -f deployment/docker-compose.yml up -d redis

# 启动应用
python -m app.main

# 另开终端：启动 Celery Worker
celery -A app.workers.celery_app worker --loglevel=info
```

### 4. 访问

| 地址 | 说明 |
|------|------|
| http://localhost:8000 | API 根路径 |
| http://localhost:8000/docs | Swagger 交互式文档 |
| http://localhost:8000/ui | Web 管理界面 |
| http://localhost:8000/health | 健康检查 |

---

## 环境配置

完整配置模板见 [`config/.env.example`](config/.env.example)。按功能分组：

| 分组 | 关键变量 | 说明 |
|------|---------|------|
| **安全** | `JWT_SECRET_KEY`, `API_KEYS` | 生产环境必须设置 JWT 密钥 |
| **高德地图** | `AMAP_API_KEY`, `AMAP_ORIGIN`, `AMAP_DESTINATION` | 通勤助手核心配置 |
| **钉钉** | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` | 消息通知 |
| **Redis/Celery** | `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | 异步任务队列 |
| **GitHub** | `GITHUB_TOKEN` | 仓库/Issue/PR 操作 |
| **Slack** | `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` | 频道消息 |
| **Brave Search** | `BRAVE_API_KEY` | 实时搜索 |
| **Notion** | `NOTION_TOKEN` | 页面/数据库管理 |
| **Google Sheets** | `GOOGLE_CREDENTIALS_PATH` | 表格操作 |
| **Context7** | `CONTEXT7_API_KEY` | 版本精确文档 |
| **Docfork** | `DOCFORK_API_KEY` | 文档语义搜索 |
| **Figma** | `FIGMA_API_KEY` | 设计稿数据 |
| **E2B** | `E2B_API_KEY` | 代码沙箱 |
| **Sentry** | `SENTRY_ACCESS_TOKEN` | 错误监控 |
| **Linear** | `LINEAR_API_KEY` | 项目管理 |
| **Composio** | `COMPOSIO_API_KEY` | 500+ 应用集成 |

---

## API 使用

所有需要认证的端点支持 JWT Token 或 API Key（`X-API-Key` Header）。

### 获取 Token

```bash
# 开发环境 Demo Token
curl -X POST "http://localhost:8000/auth/token?username=demo&password=demo"
# → {"access_token": "eyJ...", "token_type": "bearer"}
```

### 列出所有 Server

```bash
curl http://localhost:8000/mcp/servers
```

### 执行工具

```bash
AUTH="Authorization: Bearer <your_token>"

# 读取文件
curl -X POST http://localhost:8000/mcp/execute/filesystem/read_file \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"path": "README.md"}'

# 查询 Context7 文档
curl -X POST http://localhost:8000/mcp/execute/context7/query_docs \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"libraryId": "/facebook/react", "query": "useEffect cleanup"}'

# 结构化推理
curl -X POST http://localhost:8000/mcp/execute/sequential_thinking/sequential_thinking \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"thought": "分析问题：用户登录失败的可能原因...", "thoughtNumber": 1, "totalThoughts": 3, "nextThoughtNeeded": true}'

# 执行终端命令
curl -X POST http://localhost:8000/mcp/execute/desktop_commander/execute_command \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"command": "git log --oneline -5", "timeout_ms": 10000}'

# E2B 代码沙箱
curl -X POST http://localhost:8000/mcp/execute/e2b/execute_code \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"code": "print(sum(range(100)))", "language": "python"}'

# Sentry 查看 Issue
curl -X POST http://localhost:8000/mcp/execute/sentry/get_issue \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"issue_id_or_url": "123456"}'

# GitHub 搜索代码
curl -X POST http://localhost:8000/mcp/execute/github/search_code \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"q": "function main language:python"}'
```

### 异步任务

```bash
# 触发通勤检查
curl -X POST http://localhost:8000/commute/check -H "$AUTH"
# → {"task_id": "abc-123", "status": "started"}

# 查询任务状态
curl http://localhost:8000/commute/status/abc-123
```

---

## Docker 部署

### 开发环境

```bash
docker compose -f deployment/docker-compose.yml up -d
```

启动组件：Redis + App + Celery Worker + Celery Beat

### 生产环境

```bash
docker compose -f deployment/docker-compose.prod.yml up -d
```

### 单独构建镜像

```bash
docker build -f docker/Dockerfile -t mcp4coder:latest .
docker run -p 8000:8000 --env-file .env mcp4coder:latest
```

---

## 安全特性

| 特性 | 说明 |
|------|------|
| **JWT 认证** | 生产环境强制配置 `JWT_SECRET_KEY`，未设置则拒绝启动 |
| **API Key 认证** | 支持 `X-API-Key` Header 认证 |
| **Demo 端点隔离** | `/auth/token` 仅开发环境可用，生产自动禁用 |
| **CORS 限制** | 白名单模式，生产环境从 `ALLOWED_ORIGINS` 加载 |
| **安全头** | HSTS、CSP、XSS Protection、Frame Options |
| **输入净化** | 请求参数自动净化，防止注入攻击 |
| **速率限制** | 内置 RateLimiter，默认 60 req/min |
| **路径越界保护** | Filesystem/Desktop Commander 限制在 `base_path` 内 |
| **Bandit 扫描** | CI 中启用硬编码密码检测（B105/B106/B107） |

---

## 项目结构

```
mcp4coder/
├── app/
│   ├── main.py                         # FastAPI 入口 + REST API 路由
│   ├── config/
│   │   ├── settings.py                 # Pydantic Settings 配置管理
│   │   └── validators.py              # 配置校验器
│   ├── mcp/
│   │   ├── servers/                    # 26 个 MCP Server 实现
│   │   │   ├── base_server.py          # BaseMCPServer 抽象基类
│   │   │   ├── amap_server.py          # 高德地图
│   │   │   ├── dingtalk_server.py      # 钉钉
│   │   │   ├── weather_server.py       # 天气
│   │   │   ├── calendar_server.py      # 日历
│   │   │   ├── filesystem_server.py    # 文件系统
│   │   │   ├── git_server.py           # Git
│   │   │   ├── database_server.py      # 数据库
│   │   │   ├── http_client_server.py   # HTTP 客户端
│   │   │   ├── github_server.py        # GitHub
│   │   │   ├── slack_server.py         # Slack
│   │   │   ├── brave_search_server.py  # Brave 搜索
│   │   │   ├── notion_server.py        # Notion
│   │   │   ├── google_sheets_server.py # Google 表格
│   │   │   ├── browser_server.py       # 浏览器自动化
│   │   │   ├── memory_server.py        # 记忆库
│   │   │   ├── context7_server.py      # Context7 文档注入
│   │   │   ├── sequential_thinking_server.py  # 结构化推理
│   │   │   ├── desktop_commander_server.py    # 终端命令
│   │   │   ├── docfork_server.py       # Docfork 文档搜索
│   │   │   ├── deepwiki_server.py      # DeepWiki 文档转换
│   │   │   ├── figma_server.py         # Figma 设计协作
│   │   │   ├── reactbits_server.py     # ReactBits 组件库
│   │   │   ├── e2b_server.py           # E2B 代码沙箱
│   │   │   ├── sentry_server.py        # Sentry 错误监控
│   │   │   ├── linear_server.py        # Linear 项目管理
│   │   │   └── composio_server.py      # Composio 多平台集成
│   │   ├── server_factory.py           # ServerType 枚举 + 工厂
│   │   └── server_manager.py           # 进程管理 + 健康检查
│   ├── middleware/
│   │   ├── auth.py                     # JWT + API Key 认证
│   │   └── security.py                 # 安全头 + 输入净化
│   ├── services/
│   │   └── commute_service.py          # 通勤助手业务逻辑
│   ├── workers/
│   │   ├── celery_app.py               # Celery 配置
│   │   └── tasks.py                    # 异步任务定义
│   ├── monitoring/
│   │   ├── performance_monitor.py      # 性能监控
│   │   └── system_monitor.py           # 系统监控
│   └── utils/
│       ├── logger.py                   # Loguru 日志
│       ├── error_handler.py            # 统一错误处理
│       └── helpers.py                  # 工具函数
├── web/
│   ├── mcp_manager.html                # Web 管理界面
│   └── workflow_designer.html          # 可视化工作流设计器
├── tests/
│   ├── conftest.py                     # 测试 fixtures
│   ├── test_config.py                  # 配置测试
│   ├── test_mcp.py                     # MCP Server 测试
│   ├── test_integration.py            # 集成测试
│   ├── test_e2e.py                     # 端到端测试
│   ├── test_security.py               # 安全测试
│   └── test_utils.py                   # 工具函数测试
├── docs/                               # 项目文档
│   ├── quick_start_guide.md
│   ├── detailed_operating_steps.md
│   ├── deployment.md
│   ├── SECURITY_CHECKLIST.md
│   └── ...
├── dumb_mode/                          # 极简独立模式（无需 FastAPI）
│   ├── commute_assistant.py
│   └── README_DUMB.md
├── docker/
│   └── Dockerfile
├── deployment/
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── scripts/
│   └── health_check.py
├── config/
│   ├── .env.example                    # 环境变量模板
│   ├── requirements.txt
│   └── pytest.ini
├── pyproject.toml                      # 项目元数据 + 工具配置
├── .bandit.yml                         # Bandit 安全扫描配置
├── .pre-commit-config.yaml             # Pre-commit hooks
├── CHANGELOG.md
├── CONTRIBUTING.md
└── CODE_OF_CONDUCT.md
```

---

## 开发新 Server

4 步创建一个新的 MCP Server：

### 1. 创建 Server 文件

```python
# app/mcp/servers/my_server.py
from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability
from typing import Any, Dict, Optional

class MYMCPServer(BaseMCPServer):
    """命名规则：{VALUE}MCPServer，与 ServerType 枚举值对应"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 在 super().__init__ 之前提取配置
        self.api_key = config.get("api_key", "") if config else ""
        super().__init__(config)

    def register_tools(self) -> None:
        self._register_tool(MCPTool(
            name="my_tool",
            description="工具描述",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "参数说明"}
                },
                "required": ["param1"]
            },
            capability=ServerCapability.READ  # READ | WRITE | EXECUTE
        ))

    def register_resources(self) -> None:
        self._register_resource(MCPResource(
            uri="my_server://status",
            name="状态",
            description="当前状态"
        ))

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        if tool_name == "my_tool":
            return {"result": f"处理 {params['param1']}"}
        raise ValueError(f"未知工具: {tool_name}")

    async def _read_resource_content(self, resource: MCPResource) -> Any:
        if resource.uri == "my_server://status":
            return {"status": "ok"}
        raise ValueError(f"未知资源: {resource.uri}")
```

### 2. 注册到 ServerFactory

在 `app/mcp/server_factory.py` 中：

```python
# ServerType 枚举
class ServerType(Enum):
    # ... 已有枚举
    MY = "my"  # 新增

# _load_builtin_servers()
ServerType.MY: ManagedServer(
    name="my-mcp-server",
    command="python",
    args=["-m", "app.mcp.servers.my_server"],
    env={"PYTHONPATH": "."},
    working_dir=".",
    timeout=300,
    max_concurrent=10,
    auto_restart=True,
    health_check_interval=120
),
```

### 3. 添加环境变量（如需）

在 `config/.env.example` 中添加占位符。

### 4. 验证

```bash
# 语法检查
python3 -c "import ast; ast.parse(open('app/mcp/servers/my_server.py').read())"

# 运行测试
pytest tests/ -v
```

---

## Dumb 模式（极简版）

不需要 FastAPI / Celery / Redis，5 分钟上手的独立通勤助手：

```bash
cd dumb_mode
pip install -r requirements.txt
python commute_assistant.py
```

详见 [`dumb_mode/README_DUMB.md`](dumb_mode/README_DUMB.md)。

---

## 2026 MCP 生态趋势

### MCP 2025-11 规范更新：Streamable HTTP Transport

2025 年 11 月，MCP 规范引入 **Streamable HTTP Transport**，正式取代原有的 SSE（Server-Sent Events）传输层：

- **双向流式通信**：单个 HTTP 连接同时支持客户端流式输入和服务端流式输出
- **更低延迟**：消除 SSE 需要独立 POST + GET 连接的开销
- **更好的负载均衡**：标准 HTTP/2 多路复用，兼容云平台反向代理
- **向后兼容**：支持降级到旧版 SSE 传输（协商机制）

本项目计划在 v2.0 中迁移到 Streamable HTTP Transport，现有 SSE 端点保留至 v3.0。

### MCP 授权：OAuth 2.1 原生支持

MCP 规范新增 **Authorization 扩展**，定义了基于 OAuth 2.1 的标准授权流程：

| 流程 | 说明 | 适用场景 |
|------|------|---------|
| Authorization Code + PKCE | 用户级授权，支持浏览器重定向 | GitHub、Notion、Linear 等需要用户登录的服务 |
| Client Credentials | 机器对机器认证 | Cloudflare、AWS、Datadog 等服务账号 |
| Token Introspection | 令牌验证端点 | MCP Server 验证客户端提供的 Token |

本框架已在 `app/middleware/auth.py` 中实现 OAuth 2.1 Bearer Token 验证，并预留 Authorization Server Metadata 发现端点（`/.well-known/oauth-authorization-server`）。

### 远程 MCP Server 趋势

2025-2026 年，MCP Server 的部署形态正从"本地进程"向"云托管 API"演进：

| 部署形态 | 优势 | 代表产品 |
|---------|------|---------|
| **本地进程**（stdio） | 低延迟、离线可用、数据不出本地 | 高德地图、文件系统、Git |
| **远程 HTTP Server** | 无需本地安装、多用户共享、托管运维 | Cloudflare MCP、Stripe MCP、Linear MCP |
| **云端 SaaS MCP** | 官方维护、自动更新、企业级 SLA | Notion MCP Cloud、GitHub MCP Cloud |

本项目基于 FastAPI 实现 HTTP Server 模式，所有 MCP Server 均可通过统一 REST API 调用，天然支持远程部署场景。

### MCP 生态注册表

MCP Server 生态正在快速扩张，主要注册/发现平台：

| 平台 | 地址 | 特色 |
|------|------|------|
| **mcp.so** | https://mcp.so | 最大 MCP Server 目录，社区驱动 |
| **Glama AI** | https://glama.ai/mcp/servers | 带质量评分和安全审计 |
| **Smithery.ai** | https://smithery.ai | 专注企业级 MCP Server 托管 |
| **Anthropic 官方列表** | https://github.com/modelcontextprotocol/servers | 官方维护参考实现 |

截至 2026 年 Q2，上述平台合计收录 3000+ 个 MCP Server，覆盖几乎所有主流 SaaS 产品。

---

## Roadmap

### v2.0（计划 2026 Q3）

**传输层升级**
- [ ] 迁移到 Streamable HTTP Transport（MCP 2025-11 规范）
- [ ] 保留 SSE 向后兼容层
- [ ] WebSocket 传输支持（实时推送场景）

**新增 Server**
- [ ] **Cloudflare MCP Server** — Workers/D1/KV/R2/DNS 全功能管理
- [ ] **Vercel MCP Server** — 部署、域名、环境变量、日志
- [ ] **Supabase MCP Server** — PostgreSQL + Auth + Storage + Edge Functions
- [ ] **AWS MCP Server** — S3/Lambda/EC2/CloudWatch
- [ ] **Stripe MCP Server** — 支付、订阅、客户管理
- [ ] **Twilio MCP Server** — SMS/Voice/WhatsApp

**企业功能**
- [ ] Jira MCP Server（Issue/Sprint/Board）
- [ ] Confluence MCP Server（页面/空间管理）
- [ ] Datadog MCP Server（指标/日志/告警）
- [ ] Google Maps MCP Server（地点/路线/地理编码）
- [ ] OpenAPI MCP Server（Swagger 规范解析与 Mock）

### v2.1（计划 2026 Q4）

**可观测性**
- [ ] OpenTelemetry 链路追踪集成
- [ ] 每个 Tool 调用的 Span 上报
- [ ] 成本追踪（Token + API 调用费用）

**安全增强**
- [ ] OAuth 2.1 Authorization Server 发现端点
- [ ] Tool 粒度权限控制（RBAC）
- [ ] 审计日志（谁在何时调用了哪个 Tool）

**开发体验**
- [ ] MCP Server 热重载（开发模式）
- [ ] Tool 调用 Playground（浏览器内交互测试）
- [ ] 自动生成 TypeScript SDK（基于 OpenAPI 规范）

### v3.0（计划 2027 Q1）

- [ ] 多模态 Tool（图片/音频输入输出）
- [ ] 分布式 MCP Server 集群（水平扩展）
- [ ] MCP Server Marketplace（内置注册表集成）
- [ ] Agent 编排原语（基于 MCP Sampling 扩展）

---

## 文档

| 文档 | 说明 |
|------|------|
| [快速开始指南](docs/quick_start_guide.md) | 30 分钟上手教程 |
| [详细操作步骤](docs/detailed_operating_steps.md) | 完整部署和配置 |
| [部署手册](docs/deployment.md) | 生产环境部署 |
| [安全检查清单](docs/SECURITY_CHECKLIST.md) | 安全配置审核 |
| [项目总结](docs/PROJECT_SUMMARY.md) | 项目完整总结 |
| [API 文档](docs/api.md) | REST API 说明 |
| [架构设计](docs/mcp_architecture.md) | 系统架构 |
| [贡献指南](CONTRIBUTING.md) | 开发规范 |

---

## 贡献

欢迎贡献！请查阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解开发规范和提交流程。

```bash
# 安装 pre-commit hooks
pre-commit install

# 运行完整检查
black app/ && isort app/ && flake8 app/ && mypy app/ && pytest tests/
```

---

## License

[MIT License](LICENSE)
