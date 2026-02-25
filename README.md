# MCP Tool Suite (MCP工具大全)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

一个给开发者用的 **MCP (Model Context Protocol) 工具大全**，提供统一的MCP服务器集合和Web管理界面。

## 功能特性

### 核心MCP服务器

| 服务器 | 功能描述 | 工具数量 |
|--------|----------|----------|
| 🗺️ **高德地图** | 路线规划、地理编码 | 4 |
| 💬 **钉钉** | 消息推送、群通知 | 3 |
| 🌤️ **天气** | 实时天气、预报 | 3 |
| 📅 **日历** | 日程管理 | 3 |
| 📁 **文件系统** | 文件读写、目录操作 | 7 |
| 🔧 **Git** | 版本控制操作 | 9 |
| 🗄️ **数据库** | MySQL/PostgreSQL/SQLite/Redis | 7 |
| 🌐 **HTTP客户端** | 发送HTTP请求 | 5 |
| 📦 **GitHub** | 仓库管理、Issue、PR | 10 |
| 💬 **Slack** | 消息推送、频道管理 | 8 |
| 🔍 **Brave搜索** | 网页、新闻、图片、视频搜索 | 4 |
| 📝 **Notion** | 笔记、数据库、页面管理 | 7 |
| 📊 **Google表格** | 表格创建、读写 | 6 |
| 🌐 **浏览器** | 自动化浏览、截图、表单 | 9 |
| 🧠 **记忆库** | 持久化记忆、知识图谱 | 9 |

### Web管理界面

- 🖥️ **可视化界面** - 浏览所有MCP服务器
- ⚡ **在线测试** - 控制台直接执行工具
- 📚 **API文档** - 完整的REST API说明

## 快速开始

### 安装依赖

```bash
pip install -r config/requirements.txt

# 可选依赖
pip install playwright  # 浏览器自动化
pip install google-api-python-client google-auth-httplib2  # Google Sheets
pip install notional  # Notion
pip install redis pymysql psycopg2-binary  # 数据库
```

### 启动服务

```bash
python -m app.main
```

### 访问界面

- Web管理界面: http://localhost:8000/ui
- API文档: http://localhost:8000/docs

## 环境变量

```env
# GitHub
GITHUB_TOKEN=your_github_token

# Slack
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx

# Brave Search
BRAVE_API_KEY=your_brave_api_key

# Notion
NOTION_TOKEN=secret_xxx

# Google Sheets
GOOGLE_CREDENTIALS_PATH=./credentials.json
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "..."}'
```

## API使用

### 列出所有服务器

```bash
curl http://localhost:8000/mcp/servers
```

### 执行工具

```bash
# 读取文件
curl -X POST http://localhost:8000/mcp/execute/filesystem/read_file \
  -H "Content-Type: application/json" \
  -d '{"path": "README.md"}'

# GitHub搜索代码
curl -X POST http://localhost:8000/mcp/execute/github/search_code \
  -H "Content-Type: application/json" \
  -d '{"q": "function main language:python"}'

# 发送Slack消息
curl -X POST http://localhost:8000/mcp/execute/slack/post_message \
  -H "Content-Type: application/json" \
  -d '{"channel": "C123", "text": "Hello!"}'
```

## 项目结构

```
mcp4coder/
├── app/
│   ├── main.py              # FastAPI应用入口
│   ├── config/              # 配置管理
│   ├── mcp/
│   │   ├── servers/         # MCP服务器实现
│   │   │   ├── base_server.py           # 基类模板
│   │   │   ├── amap_server.py          # 高德地图
│   │   │   ├── dingtalk_server.py      # 钉钉
│   │   │   ├── weather_server.py       # 天气
│   │   │   ├── calendar_server.py      # 日历
│   │   │   ├── filesystem_server.py   # 文件系统
│   │   │   ├── git_server.py           # Git
│   │   │   ├── database_server.py     # 数据库
│   │   │   ├── http_client_server.py   # HTTP客户端
│   │   │   ├── github_server.py       # GitHub
│   │   │   ├── slack_server.py         # Slack
│   │   │   ├── brave_search_server.py # Brave搜索
│   │   │   ├── notion_server.py        # Notion
│   │   │   ├── google_sheets_server.py # Google表格
│   │   │   ├── browser_server.py      # 浏览器自动化
│   │   │   └── memory_server.py        # 记忆库
│   │   ├── server_factory.py           # 服务器工厂
│   │   └── server_manager.py          # 服务器管理
│   ├── services/           # 业务服务
│   ├── workers/            # Celery任务
│   └── utils/              # 工具函数
├── web/
│   └── mcp_manager.html    # Web管理界面
└── config/                 # 配置文件
```

## 开发新服务器

参考 `app/mcp/servers/base_server.py` 创建新的MCP服务器：

```python
from .base_server import BaseMCPServer, MCPTool, MCPResource

class MyMCPServer(BaseMCPServer):
    def register_tools(self):
        self._register_tool(MCPTool(
            name="my_tool",
            description="我的工具",
            input_schema={...}
        ))
    
    def register_resources(self):
        self._register_resource(MCPResource(...))
    
    async def execute_tool(self, tool_name, params):
        # 实现工具逻辑
        pass
    
    async def _read_resource_content(self, resource):
        # 实现资源读取
        pass
```

## License

MIT License
