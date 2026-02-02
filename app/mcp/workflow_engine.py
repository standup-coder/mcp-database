"""
MCP工作流执行引擎
基于DSL定义执行工作流任务
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from pydantic import BaseModel

from ..utils.logger import get_logger
from ..utils.exceptions import TaskExecutionError
from ..utils.error_handler import retry
from .workflow_dsl import DSLWorkflow, DSLNode, DSLNodeType
from .orchestrator import (
    MCPWorkflowEngine, 
    ExecutionContext, 
    OrchestrationResult,
    TaskType,
    TaskStatus
)
from .server_manager import server_manager

logger = get_logger(__name__)


class WorkflowExecutionContext(BaseModel):
    """工作流执行上下文"""
    execution_id: str
    workflow_id: str
    workflow_name: str
    start_time: datetime
    variables: Dict[str, Any] = {}
    node_results: Dict[str, Any] = {}
    execution_path: List[str] = []
    status: TaskStatus = TaskStatus.PENDING
    current_node: Optional[str] = None
    error: Optional[str] = None


class DSLWorkflowExecutor:
    """DSL工作流执行器"""
    
    def __init__(self, workflow_engine: MCPWorkflowEngine):
        self.workflow_engine = workflow_engine
        self.active_executions: Dict[str, WorkflowExecutionContext] = {}
        
        # 注册DSL特定的步骤处理器
        self._register_dsl_handlers()
    
    def _register_dsl_handlers(self):
        """注册DSL节点类型处理器"""
        self.workflow_engine.register_step_handler(
            TaskType.MCP_SERVER,
            self._handle_mcp_tool_node
        )
        self.workflow_engine.register_step_handler(
            TaskType.CONDITION,
            self._handle_condition_node
        )
        self.workflow_engine.register_step_handler(
            TaskType.TRANSFORM,
            self._handle_transform_node
        )
    
    async def execute_workflow(
        self,
        workflow: DSLWorkflow,
        variables: Dict[str, Any] = None
    ) -> OrchestrationResult:
        """执行DSL工作流"""
        # 创建执行上下文
        context = WorkflowExecutionContext(
            execution_id=f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(workflow.id)}",
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            start_time=datetime.now(),
            variables=variables or workflow.variables.copy()
        )
        
        self.active_executions[context.execution_id] = context
        logger.info(f"开始执行工作流: {workflow.name}", execution_id=context.execution_id)
        
        result = OrchestrationResult(
            execution_id=context.execution_id,
            workflow_id=workflow.id,
            status=TaskStatus.RUNNING,
            start_time=context.start_time
        )
        
        try:
            # 按拓扑顺序执行节点
            await self._execute_nodes_in_order(workflow, context)
            
            result.status = TaskStatus.SUCCESS
            logger.info(f"工作流执行成功: {workflow.name}")
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            context.error = str(e)
            logger.error(f"工作流执行失败: {workflow.name}", error=str(e))
            
        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            result.step_results = context.node_results
            
            # 清理执行上下文
            if context.execution_id in self.active_executions:
                del self.active_executions[context.execution_id]
        
        return result
    
    async def _execute_nodes_in_order(
        self,
        workflow: DSLWorkflow,
        context: WorkflowExecutionContext
    ):
        """按顺序执行工作流节点"""
        # 构建执行顺序（拓扑排序）
        execution_order = self._build_execution_order(workflow)
        
        for node_id in execution_order:
            node = self._find_node_by_id(workflow, node_id)
            if not node:
                continue
                
            context.current_node = node_id
            context.execution_path.append(node_id)
            
            # 执行节点
            await self._execute_single_node(node, workflow, context)
    
    def _build_execution_order(self, workflow: DSLWorkflow) -> List[str]:
        """构建节点执行顺序（拓扑排序）"""
        # 简单的拓扑排序实现
        visited: Set[str] = set()
        order: List[str] = []
        
        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            node = self._find_node_by_id(workflow, node_id)
            if node:
                # 先执行前置节点
                for next_node_id in node.next_nodes:
                    dfs(next_node_id)
            
            order.append(node_id)
        
        # 从起始节点开始DFS
        dfs(workflow.start_node)
        
        # 反转得到正确的执行顺序
        return list(reversed(order))
    
    async def _execute_single_node(
        self,
        node: DSLNode,
        workflow: DSLWorkflow,
        context: WorkflowExecutionContext
    ):
        """执行单个节点"""
        logger.debug(f"执行节点: {node.name} ({node.type.value})", node_id=node.id)
        
        try:
            if node.type == DSLNodeType.START:
                # 起始节点 - 初始化工作流
                await self._handle_start_node(node, context)
                
            elif node.type == DSLNodeType.END:
                # 结束节点 - 完成工作流
                await self._handle_end_node(node, context)
                
            elif node.type == DSLNodeType.MCP_TOOL:
                # MCP工具节点
                result = await self._handle_mcp_tool_node(node, {}, context)
                context.node_results[node.id] = result
                
            elif node.type == DSLNodeType.CONDITION:
                # 条件节点
                result = await self._handle_condition_node(node, {}, context)
                context.node_results[node.id] = result
                
            elif node.type == DSLNodeType.TRANSFORM:
                # 数据转换节点
                result = await self._handle_transform_node(node, {}, context)
                context.node_results[node.id] = result
                
            else:
                raise TaskExecutionError(f"不支持的节点类型: {node.type}")
                
        except Exception as e:
            logger.error(f"节点执行失败: {node.name}", error=str(e))
            raise TaskExecutionError(f"节点 {node.name} 执行失败: {str(e)}")
    
    async def _handle_start_node(
        self,
        node: DSLNode,
        context: WorkflowExecutionContext
    ):
        """处理起始节点"""
        logger.debug("处理起始节点")
        context.node_results[node.id] = {
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_end_node(
        self,
        node: DSLNode,
        context: WorkflowExecutionContext
    ):
        """处理结束节点"""
        logger.debug("处理结束节点")
        context.node_results[node.id] = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "execution_path": context.execution_path.copy()
        }
    
    async def _handle_mcp_tool_node(
        self,
        node: DSLNode,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """处理MCP工具节点"""
        server_name = node.config.get("server")
        tool_name = node.config.get("tool")
        
        if not server_name or not tool_name:
            raise TaskExecutionError("MCP工具节点缺少server或tool配置")
        
        # 解析输入参数
        resolved_inputs = self._resolve_node_inputs(node, context)
        
        # 调用MCP服务器
        try:
            # 这里应该调用实际的MCP服务器
            # 模拟调用结果
            result = {
                "server": server_name,
                "tool": tool_name,
                "inputs": resolved_inputs,
                "result": f"模拟执行结果_{datetime.now().strftime('%H%M%S')}",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.debug(f"MCP工具调用成功: {server_name}.{tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"MCP工具调用失败: {server_name}.{tool_name}", error=str(e))
            raise TaskExecutionError(f"MCP工具调用失败: {str(e)}")
    
    async def _handle_condition_node(
        self,
        node: DSLNode,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """处理条件节点"""
        condition = node.condition
        if not condition:
            raise TaskExecutionError("条件节点缺少条件配置")
        
        # 解析条件表达式
        left_value = self._resolve_condition_value(condition.get("left"), context)
        right_value = self._resolve_condition_value(condition.get("right"), context)
        operator = condition.get("operator")
        
        # 执行条件判断
        condition_result = self._evaluate_condition(left_value, operator, right_value)
        
        result = {
            "condition": condition,
            "result": condition_result,
            "evaluated_values": {
                "left": left_value,
                "right": right_value
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.debug(f"条件判断结果: {condition_result}")
        return result
    
    async def _handle_transform_node(
        self,
        node: DSLNode,
        inputs: Dict[str, Any],
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """处理数据转换节点"""
        script = node.config.get("script", "")
        if not script:
            raise TaskExecutionError("转换节点缺少脚本配置")
        
        # 解析输入数据
        resolved_inputs = self._resolve_node_inputs(node, context)
        
        # 执行转换脚本（简化实现）
        try:
            # 这里应该执行实际的脚本转换
            # 模拟转换结果
            transformed_data = {
                "input_data": resolved_inputs,
                "transformation": "applied",
                "result": f"转换结果_{datetime.now().strftime('%H%M%S')}",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.debug("数据转换执行成功")
            return transformed_data
            
        except Exception as e:
            logger.error("数据转换执行失败", error=str(e))
            raise TaskExecutionError(f"数据转换失败: {str(e)}")
    
    def _resolve_node_inputs(
        self,
        node: DSLNode,
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """解析节点输入参数"""
        resolved = {}
        
        for key, value_expr in node.inputs.items():
            # 解析表达式 ${variable} 或 ${node_id.output_key}
            if value_expr.startswith('${') and value_expr.endswith('}'):
                expr_content = value_expr[2:-1]
                
                # 处理变量引用
                if expr_content in context.variables:
                    resolved[key] = context.variables[expr_content]
                
                # 处理节点结果引用
                elif '.' in expr_content:
                    parts = expr_content.split('.', 1)
                    node_id, output_key = parts[0], parts[1]
                    if node_id in context.node_results:
                        node_result = context.node_results[node_id]
                        if isinstance(node_result, dict) and output_key in node_result:
                            resolved[key] = node_result[output_key]
                        else:
                            resolved[key] = node_result
                    else:
                        resolved[key] = None
                else:
                    resolved[key] = None
            else:
                resolved[key] = value_expr
        
        return resolved
    
    def _resolve_condition_value(
        self,
        value_expr: Any,
        context: WorkflowExecutionContext
    ) -> Any:
        """解析条件值表达式"""
        if isinstance(value_expr, str) and value_expr.startswith('${') and value_expr.endswith('}'):
            expr_content = value_expr[2:-1]
            # 简单的变量解析
            if expr_content in context.variables:
                return context.variables[expr_content]
            return None
        return value_expr
    
    def _evaluate_condition(
        self,
        left_value: Any,
        operator: str,
        right_value: Any
    ) -> bool:
        """评估条件表达式"""
        try:
            if operator == "==":
                return left_value == right_value
            elif operator == "!=":
                return left_value != right_value
            elif operator == ">":
                return left_value > right_value
            elif operator == "<":
                return left_value < right_value
            elif operator == ">=":
                return left_value >= right_value
            elif operator == "<=":
                return left_value <= right_value
            elif operator == "contains":
                return right_value in left_value if left_value else False
            elif operator == "in":
                return left_value in right_value if right_value else False
            else:
                raise TaskExecutionError(f"不支持的操作符: {operator}")
                
        except Exception as e:
            logger.error(f"条件评估失败: {operator}", error=str(e))
            return False
    
    def _find_node_by_id(self, workflow: DSLWorkflow, node_id: str) -> Optional[DSLNode]:
        """根据ID查找节点"""
        for node in workflow.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecutionContext]:
        """获取执行状态"""
        return self.active_executions.get(execution_id)
    
    def list_active_executions(self) -> Dict[str, WorkflowExecutionContext]:
        """列出活跃的执行"""
        return self.active_executions.copy()


# 全局工作流执行器实例
dsl_executor: Optional[DSLWorkflowExecutor] = None


async def get_dsl_executor() -> DSLWorkflowExecutor:
    """获取DSL工作流执行器实例"""
    global dsl_executor
    if dsl_executor is None:
        from .orchestrator import mcp_orchestrator
        dsl_executor = DSLWorkflowExecutor(mcp_orchestrator)
    return dsl_executor