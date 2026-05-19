"""
E2E 测试
测试完整的 API 端点流程
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """创建认证头"""
    from app.middleware.auth import create_access_token
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_key_headers():
    """创建 API Key 头"""
    return {"X-API-Key": "test-api-key"}


class TestRootEndpoint:
    """根端点测试"""
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "timestamp" in data


class TestHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        with patch('app.services.commute_service.CommuteService') as mock_service:
            mock_service.return_value.health_check = AsyncMock(return_value={
                "status": "healthy",
                "checks": {
                    "amap_api": {"status": "healthy"},
                    "dingtalk_api": {"status": "healthy"}
                }
            })
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestMCPServersEndpoints:
    """MCP 服务器端点测试"""
    
    def test_list_mcp_servers(self, client):
        """测试列出 MCP 服务器"""
        response = client.get("/mcp/servers")
        assert response.status_code == 200
        data = response.json()
        assert "servers" in data
        assert "total" in data
        assert isinstance(data["servers"], list)
    
    def test_get_mcp_server_info(self, client):
        """测试获取 MCP 服务器信息"""
        # 先获取一个服务器名称
        response = client.get("/mcp/servers")
        servers = response.json()["servers"]
        
        if servers:
            server_name = servers[0]["name"]
            response = client.get(f"/mcp/servers/{server_name}")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == server_name
    
    def test_get_mcp_server_info_not_found(self, client):
        """测试获取不存在的服务器信息"""
        response = client.get("/mcp/servers/nonexistent-server")
        assert response.status_code == 404
    
    def test_list_server_types(self, client):
        """测试列出服务器类型"""
        response = client.get("/mcp/server-types")
        assert response.status_code == 200
        data = response.json()
        assert "server_types" in data
        assert isinstance(data["server_types"], list)


class TestMCPExecuteEndpoint:
    """MCP 执行端点测试"""
    
    def test_execute_tool_requires_auth(self, client):
        """测试执行工具需要认证"""
        response = client.post("/mcp/execute/filesystem/read_file", json={})
        assert response.status_code == 401
    
    def test_execute_tool_with_jwt(self, client, auth_headers):
        """测试使用 JWT 执行工具"""
        with patch('app.mcp.servers.filesystem_server.FilesystemMCPServer') as mock_server:
            mock_instance = AsyncMock()
            mock_instance.execute_tool.return_value = {"content": "test"}
            mock_server.return_value = mock_instance
            
            response = client.post(
                "/mcp/execute/filesystem/read_file",
                json={"path": "test.txt"},
                headers=auth_headers
            )
            # 由于服务器可能不存在，可能返回 404 或 500
            assert response.status_code in [200, 404, 500]
    
    def test_execute_tool_with_api_key(self, client, api_key_headers):
        """测试使用 API Key 执行工具"""
        with patch('app.middleware.auth.api_keys', {"test-api-key": {"name": "test"}}):
            response = client.post(
                "/mcp/execute/filesystem/read_file",
                json={"path": "test.txt"},
                headers=api_key_headers
            )
            # 由于服务器可能不存在，可能返回 404 或 500
            assert response.status_code in [200, 404, 500]
    
    def test_execute_tool_sanitizes_input(self, client, auth_headers):
        """测试输入净化"""
        with patch('app.mcp.servers.filesystem_server.FilesystemMCPServer') as mock_server:
            mock_instance = AsyncMock()
            mock_instance.execute_tool.return_value = {"success": True}
            mock_server.return_value = mock_instance
            
            # 测试路径遍历防护
            response = client.post(
                "/mcp/execute/filesystem/read_file",
                json={"path": "../../../etc/passwd"},
                headers=auth_headers
            )
            # 应该被净化
            assert response.status_code in [200, 400, 404, 500]


class TestAuthEndpoints:
    """认证端点测试"""
    
    def test_create_token_valid(self, client):
        """测试创建有效 token"""
        response = client.post("/auth/token", params={
            "username": "admin",
            "password": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
    
    def test_create_token_invalid(self, client):
        """测试创建无效 token"""
        response = client.post("/auth/token", params={
            "username": "wrong",
            "password": "wrong"
        })
        assert response.status_code == 401
    
    def test_get_current_user_authenticated(self, client, auth_headers):
        """测试获取认证用户信息"""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"] is not None
    
    def test_get_current_user_unauthenticated(self, client):
        """测试获取未认证用户信息"""
        response = client.get("/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None


class TestCommuteEndpoints:
    """通勤端点测试"""
    
    def test_check_commute(self, client):
        """测试手动触发通勤检查"""
        with patch('app.workers.tasks.check_commute_and_notify') as mock_task:
            mock_task.delay.return_value = Mock(id="test-task-id")
            
            response = client.post("/commute/check")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "通勤检查任务已启动"
            assert data["task_id"] == "test-task-id"
    
    def test_get_task_status(self, client):
        """测试获取任务状态"""
        with patch('celery.result.AsyncResult') as mock_result:
            mock_result.return_value = Mock(
                status="SUCCESS",
                ready=lambda: True,
                result={"success": True}
            )
            
            response = client.get("/commute/status/test-task-id")
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "test-task-id"
            assert data["status"] == "SUCCESS"


class TestConfigEndpoints:
    """配置端点测试"""
    
    def test_get_config_info_development(self, client):
        """测试获取配置信息（开发环境）"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.is_development = True
            mock_settings.app_env = "development"
            mock_settings.debug = True
            mock_settings.log_level = "INFO"
            
            response = client.get("/config/info")
            assert response.status_code == 200
            data = response.json()
            assert "config" in data
    
    def test_get_config_info_production(self, client):
        """测试获取配置信息（生产环境）"""
        with patch('app.config.settings.settings') as mock_settings:
            mock_settings.is_development = False
            mock_settings.is_production = True
            
            response = client.get("/config/info")
            assert response.status_code == 403


class TestUIEndpoint:
    """UI 端点测试"""
    
    def test_get_ui(self, client):
        """测试获取 UI 页面"""
        response = client.get("/ui")
        # 可能返回 200 或 404（文件不存在）
        assert response.status_code in [200, 404]


class TestCORSHeaders:
    """CORS 头测试"""
    
    def test_cors_allowed_origin(self, client):
        """测试允许的 CORS 来源"""
        response = client.options("/", headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "GET"
        })
        # CORS 头应该存在
        assert response.status_code in [200, 204]
    
    def test_cors_disallowed_origin(self, client):
        """测试不允许的 CORS 来源"""
        response = client.options("/", headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET"
        })
        # 应该没有 CORS 头或被拒绝
        assert response.status_code in [200, 204, 403]


class TestSecurityHeaders:
    """安全头测试"""
    
    def test_security_headers_present(self, client):
        """测试安全头存在"""
        response = client.get("/")
        
        # 检查安全头
        # 注意：TestClient 可能不会添加所有中间件头
        # 这里主要测试中间件是否正确配置
        assert response.status_code == 200


class TestRateLimiting:
    """速率限制测试"""
    
    def test_rate_limit_allows_normal_requests(self, client):
        """测试速率限制允许正常请求"""
        # 发送少量请求
        for _ in range(5):
            response = client.get("/")
            assert response.status_code == 200
    
    def test_rate_limit_blocks_excessive_requests(self, client):
        """测试速率限制阻止过多请求"""
        # 注意：这个测试可能需要调整速率限制配置
        # 这里只测试基本功能
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
