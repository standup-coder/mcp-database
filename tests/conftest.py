"""
Pytest 配置文件
提供共享的测试 fixtures
"""

import os
import pytest
from unittest.mock import patch, AsyncMock


@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    test_env = {
        "APP_ENV": "test",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "AMAP_API_KEY": "test_amap_key",
        "AMAP_ORIGIN": "116.481485,39.990464",
        "AMAP_DESTINATION": "116.481485,39.990464",
        "DINGTALK_WEBHOOK_URL": "https://test.webhook.url",
        "DINGTALK_SECRET": "test_secret",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "CELERY_BROKER_URL": "redis://localhost:6379/1",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
        "JWT_SECRET_KEY": "test-secret-key-for-testing",
        "API_KEYS": "test-key:test-user",
    }
    
    with patch.dict(os.environ, test_env, clear=False):
        yield


@pytest.fixture
def mock_redis():
    """Mock Redis 客户端"""
    with patch('redis.Redis') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_celery():
    """Mock Celery 应用"""
    with patch('celery.Celery') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_httpx():
    """Mock HTTPX 客户端"""
    with patch('httpx.AsyncClient') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_mcp_tool():
    """示例 MCP 工具"""
    from app.mcp.servers.base_server import MCPTool, ServerCapability
    
    return MCPTool(
        name="test_tool",
        description="Test tool for testing",
        input_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Test parameter"},
                "param2": {"type": "integer", "description": "Another parameter", "default": 0}
            },
            "required": ["param1"]
        },
        capability=ServerCapability.READ
    )


@pytest.fixture
def sample_mcp_resource():
    """示例 MCP 资源"""
    from app.mcp.servers.base_server import MCPResource
    
    return MCPResource(
        uri="test://resource",
        name="test_resource",
        description="Test resource for testing",
        mime_type="text/plain"
    )


@pytest.fixture
def sample_server_config():
    """示例服务器配置"""
    from app.mcp.server_manager import ManagedServer
    
    return ManagedServer(
        name="test-server",
        command="python",
        args=["-c", "print('hello')"],
        timeout=300,
        max_concurrent=5,
        auto_restart=True,
        health_check_interval=60
    )


@pytest.fixture
def sample_workflow_definition():
    """示例工作流定义"""
    from app.mcp.orchestrator import WorkflowDefinition, WorkflowStep, TaskType
    
    step = WorkflowStep(
        name="test-step",
        type=TaskType.MCP_SERVER,
        config={"server": "test-server", "tool": "test-tool"}
    )
    
    return WorkflowDefinition(
        name="test-workflow",
        description="Test workflow",
        steps=[step]
    )


@pytest.fixture
def mock_amap_response():
    """Mock 高德地图 API 响应"""
    return {
        "status": "1",
        "info": "OK",
        "route": {
            "origin": "116.481485,39.990464",
            "destination": "116.481485,39.990464",
            "paths": [{
                "distance": "15000",
                "duration": "1800",
                "traffic_lights": "8",
                "tolls": "0",
                "toll_distance": "0",
                "steps": []
            }]
        }
    }


@pytest.fixture
def mock_dingtalk_response():
    """Mock 钉钉 API 响应"""
    return {
        "errcode": 0,
        "errmsg": "ok",
        "msgid": "test_message_id"
    }


@pytest.fixture
def mock_github_response():
    """Mock GitHub API 响应"""
    return {
        "login": "testuser",
        "id": 12345,
        "name": "Test User",
        "email": "test@example.com"
    }


@pytest.fixture
def mock_slack_response():
    """Mock Slack API 响应"""
    return {
        "ok": True,
        "channel": "C1234567890",
        "ts": "1234567890.123456",
        "message": {
            "text": "Test message"
        }
    }


@pytest.fixture
def mock_notion_response():
    """Mock Notion API 响应"""
    return {
        "object": "page",
        "id": "test-page-id",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
        "parent": {
            "type": "database_id",
            "database_id": "test-database-id"
        }
    }


@pytest.fixture
def mock_google_sheets_response():
    """Mock Google Sheets API 响应"""
    return {
        "spreadsheetId": "test-spreadsheet-id",
        "properties": {
            "title": "Test Spreadsheet"
        },
        "sheets": [{
            "properties": {
                "sheetId": 0,
                "title": "Sheet1"
            }
        }]
    }
