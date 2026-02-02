"""
MCP模块测试
测试MCP编排器、服务器管理器等相关功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.mcp.orchestrator import (
    MCPWorkflowEngine, 
    WorkflowDefinition, 
    WorkflowStep, 
    TaskType, 
    TaskStatus
)
from app.mcp.server_manager import (
    MCPServerManager, 
    ManagedServer, 
    ServerStatus
)
from app.mcp.server_factory import ServerFactory, ServerType
from app.mcp.workflow_dsl import (
    WorkflowDSLParser, 
    WorkflowBuilder,
    DSLWorkflow
)


class TestMCPWorkflowEngine:
    """MCP工作流引擎测试"""
    
    @pytest.fixture
    def workflow_engine(self):
        """工作流引擎实例"""
        return MCPWorkflowEngine()
    
    def test_workflow_engine_initialization(self, workflow_engine):
        """测试工作流引擎初始化"""
        assert len(workflow_engine.servers) == 0
        assert len(workflow_engine.active_executions) == 0
        assert len(workflow_engine.workflow_definitions) == 0
        assert len(workflow_engine.step_handlers) == 0
    
    @pytest.mark.asyncio
    async def test_register_server(self, workflow_engine):
        """测试注册服务器"""
        # 测试有效的服务器配置
        server_config = ManagedServer(
            name="test-server",
            command="python",
            args=["-c", "print('hello')"]
        )
        
        result = await workflow_engine.register_server(server_config)
        assert result is True
        assert "test-server" in workflow_engine.servers
    
    @pytest.mark.asyncio
    async def test_register_invalid_server(self, workflow_engine):
        """测试注册无效服务器"""
        # 测试无效的服务器配置（缺少命令）
        invalid_server = ManagedServer(
            name="invalid-server",
            command="",  # 空命令
            args=[]
        )
        
        result = await workflow_engine.register_server(invalid_server)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_register_workflow(self, workflow_engine):
        """测试注册工作流"""
        # 创建测试工作流
        step = WorkflowStep(
            name="test-step",
            type=TaskType.MCP_SERVER,
            config={"server": "test-server", "tool": "test-tool"}
        )
        
        workflow = WorkflowDefinition(
            name="test-workflow",
            steps=[step]
        )
        
        # 先注册服务器
        server_config = ManagedServer(name="test-server", command="python")
        await workflow_engine.register_server(server_config)
        
        # 注册工作流
        result = await workflow_engine.register_workflow(workflow)
        assert result is True
        assert workflow.id in workflow_engine.workflow_definitions
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, workflow_engine):
        """测试执行工作流"""
        # 注册服务器和工作流
        server_config = ManagedServer(name="test-server", command="python")
        await workflow_engine.register_server(server_config)
        
        step = WorkflowStep(
            name="test-step",
            type=TaskType.MCP_SERVER,
            config={"server": "test-server", "tool": "test-tool"}
        )
        
        workflow = WorkflowDefinition(
            name="test-workflow",
            steps=[step]
        )
        
        await workflow_engine.register_workflow(workflow)
        
        # 执行工作流
        result = await workflow_engine.execute_workflow(workflow.id)
        
        assert result.status in [TaskStatus.SUCCESS, TaskStatus.FAILED]
        assert result.workflow_id == workflow.id
        assert result.duration is not None


class TestMCPServerManager:
    """MCP服务器管理器测试"""
    
    @pytest.fixture
    def server_manager(self):
        """服务器管理器实例"""
        return MCPServerManager()
    
    def test_server_manager_initialization(self, server_manager):
        """测试服务器管理器初始化"""
        assert len(server_manager.servers) == 0
        assert len(server_manager.managed_configs) == 0
        assert len(server_manager.health_check_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_register_server_config(self, server_manager):
        """测试注册服务器配置"""
        config = ManagedServer(
            name="test-server",
            command="python",
            args=["-c", "print('test')"],
            timeout=300
        )
        
        result = await server_manager.register_server(config)
        assert result is True
        assert "test-server" in server_manager.managed_configs
        assert "test-server" in server_manager.servers
    
    @pytest.mark.asyncio
    async def test_server_health_check(self, server_manager):
        """测试服务器健康检查"""
        config = ManagedServer(name="test-server", command="python")
        await server_manager.register_server(config)
        
        # 获取健康状态
        health = await server_manager.get_server_health("test-server")
        
        assert health is not None
        assert health.status in [ServerStatus.STOPPED, ServerStatus.ERROR]


class TestServerFactory:
    """服务器工厂测试"""
    
    @pytest.fixture
    def server_factory(self):
        """服务器工厂实例"""
        return ServerFactory()
    
    def test_server_factory_initialization(self, server_factory):
        """测试服务器工厂初始化"""
        # 检查内置服务器配置是否加载
        configs = server_factory.list_available_servers()
        assert len(configs) >= 2  # 至少应该有高德和钉钉服务器
        assert "amap-mcp-server" in configs
        assert "dingtalk-mcp-server" in configs
    
    def test_get_server_config(self, server_factory):
        """测试获取服务器配置"""
        config = server_factory.get_server_config("amap-mcp-server")
        assert config is not None
        assert config.name == "amap-mcp-server"
        assert config.command == "python"
    
    def test_create_server_instance(self, server_factory):
        """测试创建服务器实例"""
        instance = server_factory.create_server_instance("amap-mcp-server")
        assert instance is not None
        assert isinstance(instance, ManagedServer)
        assert instance.name == "amap-mcp-server"
    
    def test_validate_server_config(self, server_factory):
        """测试服务器配置验证"""
        # 有效配置
        valid_config = ManagedServer(
            name="valid-server",
            command="python",
            timeout=300,
            max_concurrent=5,
            health_check_interval=60
        )
        assert server_factory.validate_server_config(valid_config) is True
        
        # 无效配置
        invalid_config = ManagedServer(
            name="",  # 空名称
            command="",
            timeout=-1,  # 负数超时
            max_concurrent=0,  # 零并发
            health_check_interval=0  # 零间隔
        )
        assert server_factory.validate_server_config(invalid_config) is False


class TestWorkflowDSL:
    """工作流DSL测试"""
    
    def test_workflow_builder_basic(self):
        """测试工作流构建器基础功能"""
        builder = WorkflowBuilder("test-workflow")
        
        workflow = (builder
            .add_start_node("Start", "开始节点")
            .add_mcp_tool_node(
                name="Test Tool",
                server="test-server",
                tool="test-tool"
            )
            .add_end_node("End", "结束节点"))
        
        built_workflow = workflow.build()
        
        assert isinstance(built_workflow, DSLWorkflow)
        assert built_workflow.name == "test-workflow"
        assert len(built_workflow.nodes) == 3
        assert built_workflow.start_node is not None
    
    def test_workflow_parser_yaml(self):
        """测试YAML工作流解析"""
        yaml_content = """
name: "test-workflow"
description: "测试工作流"
version: "1.0.0"
start_node: "start"
nodes:
  - id: "start"
    type: "start"
    name: "开始"
  - id: "end"
    type: "end"
    name: "结束"
"""
        
        workflow = WorkflowDSLParser.parse_yaml(yaml_content)
        assert workflow.name == "test-workflow"
        assert len(workflow.nodes) == 2
        assert workflow.start_node == "start"
    
    def test_workflow_parser_json(self):
        """测试JSON工作流解析"""
        json_content = '''
{
    "name": "test-workflow",
    "start_node": "start",
    "nodes": [
        {
            "id": "start",
            "type": "start",
            "name": "开始"
        }
    ]
}
'''
        
        workflow = WorkflowDSLParser.parse_json(json_content)
        assert workflow.name == "test-workflow"
        assert len(workflow.nodes) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])