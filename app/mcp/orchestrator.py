"""
MCP编排器核心框架
提供MCP服务编排、工作流执行和任务调度功能
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from ..utils.logger import get_logger
from ..utils.exceptions import MCPBaseException
from ..utils.error_handler import retry, DEFAULT_RETRY_CONFIG

logger = get_logger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型枚举"""
    MCP_SERVER = "mcp_server"
    CONDITION = "condition"
    TRANSFORM = "transform"
    NOTIFICATION = "notification"


class MCPToolCall(BaseModel):
    """MCP工具调用定义"""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    server: str = Field(..., description="MCP服务器名称")


class WorkflowStep(BaseModel):
    """工作流步骤定义"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: TaskType
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, str] = Field(default_factory=dict)
    outputs: List[str] = Field(default_factory=list)
    condition: Optional[str] = None
    retry_config: Optional[Dict[str, Any]] = None
    timeout: int = 300  # 超时时间（秒）


class WorkflowDefinition(BaseModel):
    """工作流定义"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0.0"
    steps: List[WorkflowStep]
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ExecutionContext(BaseModel):
    """执行上下文"""
    workflow_id: str
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    variables: Dict[str, Any] = Field(default_factory=dict)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING


class MCPServer(BaseModel):
    """MCP服务器定义"""
    name: str
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    working_dir: Optional[str] = None
    timeout: int = 300


class OrchestrationResult(BaseModel):
    """编排执行结果"""
    execution_id: str
    workflow_id: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    step_results: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class MCPWorkflowEngine:
    """MCP工作流引擎"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.step_handlers: Dict[TaskType, Callable] = {}
        
    async def register_server(self, server: MCPServer) -> bool:
        """注册MCP服务器"""
        try:
            # 验证服务器配置
            if not server.command:
                raise ValueError("服务器命令不能为空")
            
            self.servers[server.name] = server
            logger.info(f"MCP服务器注册成功: {server.name}")
            return True
            
        except Exception as e:
            logger.error(f"MCP服务器注册失败: {server.name}", error=str(e))
            return False
    
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """注册工作流定义"""
        try:
            # 验证工作流定义
            if not workflow.steps:
                raise ValueError("工作流至少需要一个步骤")
            
            # 验证步骤引用的服务器是否存在
            for step in workflow.steps:
                if step.type == TaskType.MCP_SERVER:
                    server_name = step.config.get('server')
                    if server_name and server_name not in self.servers:
                        raise ValueError(f"引用的服务器不存在: {server_name}")
            
            self.workflow_definitions[workflow.id] = workflow
            logger.info(f"工作流注册成功: {workflow.name} (v{workflow.version})")
            return True
            
        except Exception as e:
            logger.error(f"工作流注册失败: {workflow.name}", error=str(e))
            return False
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        initial_variables: Dict[str, Any] = None
    ) -> OrchestrationResult:
        """执行工作流"""
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        workflow = self.workflow_definitions[workflow_id]
        execution_context = ExecutionContext(
            workflow_id=workflow_id,
            variables=initial_variables or {}
        )
        
        self.active_executions[execution_context.execution_id] = execution_context
        logger.info(f"开始执行工作流: {workflow.name}", execution_id=execution_context.execution_id)
        
        result = OrchestrationResult(
            execution_id=execution_context.execution_id,
            workflow_id=workflow_id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # 顺序执行工作流步骤
            for step in workflow.steps:
                await self._execute_step(step, execution_context)
            
            result.status = TaskStatus.SUCCESS
            logger.info(f"工作流执行成功: {workflow.name}")
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            logger.error(f"工作流执行失败: {workflow.name}", error=str(e))
            
        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            result.step_results = execution_context.step_results
            
            # 清理执行上下文
            if execution_context.execution_id in self.active_executions:
                del self.active_executions[execution_context.execution_id]
        
        return result
    
    async def _execute_step(
        self, 
        step: WorkflowStep, 
        context: ExecutionContext
    ) -> Any:
        """执行单个工作流步骤"""
        logger.debug(f"执行步骤: {step.name}", step_id=step.id)
        
        try:
            # 处理输入变量映射
            resolved_inputs = self._resolve_inputs(step.inputs, context)
            
            # 根据步骤类型执行相应处理
            handler = self.step_handlers.get(step.type)
            if not handler:
                raise ValueError(f"不支持的步骤类型: {step.type}")
            
            # 执行步骤（带重试机制）
            retry_config = step.retry_config or DEFAULT_RETRY_CONFIG.__dict__
            
            @retry(max_attempts=retry_config.get('max_attempts', 3))
            async def execute_with_retry():
                return await handler(step, resolved_inputs, context)
            
            result = await execute_with_retry()
            
            # 存储输出结果
            if step.outputs:
                for output_key in step.outputs:
                    context.step_results[f"{step.id}.{output_key}"] = result.get(output_key) if isinstance(result, dict) else result
            else:
                context.step_results[step.id] = result
            
            logger.debug(f"步骤执行成功: {step.name}")
            return result
            
        except Exception as e:
            logger.error(f"步骤执行失败: {step.name}", error=str(e))
            raise
    
    def _resolve_inputs(
        self, 
        inputs: Dict[str, str], 
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """解析输入变量"""
        resolved = {}
        for key, value_expr in inputs.items():
            # 简单的变量替换 ${variable_name}
            if value_expr.startswith('${') and value_expr.endswith('}'):
                var_name = value_expr[2:-1]
                if var_name in context.variables:
                    resolved[key] = context.variables[var_name]
                elif var_name in context.step_results:
                    resolved[key] = context.step_results[var_name]
                else:
                    resolved[key] = None  # 或抛出异常
            else:
                resolved[key] = value_expr
        return resolved
    
    def register_step_handler(
        self, 
        task_type: TaskType, 
        handler: Callable
    ) -> None:
        """注册步骤处理器"""
        self.step_handlers[task_type] = handler
        logger.debug(f"注册步骤处理器: {task_type.value}")


# 全局编排器实例
mcp_orchestrator = MCPWorkflowEngine()