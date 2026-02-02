"""
MCP工作流DSL（领域特定语言）
提供声明式的工作流定义语法和解析器
"""

import yaml
import json
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

from ..utils.logger import get_logger
from ..utils.exceptions import ConfigValidationError

logger = get_logger(__name__)


class DSLNodeType(Enum):
    """DSL节点类型枚举"""
    START = "start"
    END = "end"
    MCP_TOOL = "mcp_tool"
    CONDITION = "condition"
    TRANSFORM = "transform"
    PARALLEL = "parallel"
    LOOP = "loop"


class DSLConditionOperator(Enum):
    """条件操作符枚举"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    IN = "in"


class DSLNode(BaseModel):
    """DSL节点定义"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: DSLNodeType
    name: str
    description: str = ""
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, str] = Field(default_factory=dict)
    outputs: List[str] = Field(default_factory=list)
    next_nodes: List[str] = Field(default_factory=list)
    condition: Optional[Dict[str, Any]] = None
    retry_config: Optional[Dict[str, Any]] = None
    timeout: int = 300


class DSLWorkflow(BaseModel):
    """DSL工作流定义"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0.0"
    nodes: List[DSLNode]
    start_node: str
    end_nodes: List[str] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('nodes')
    def validate_nodes(cls, nodes):
        if not nodes:
            raise ValueError("工作流至少需要一个节点")
        return nodes
    
    @validator('start_node')
    def validate_start_node(cls, start_node, values):
        nodes = values.get('nodes', [])
        node_ids = [node.id for node in nodes]
        if start_node not in node_ids:
            raise ValueError(f"起始节点不存在: {start_node}")
        return start_node


class WorkflowDSLParser:
    """工作流DSL解析器"""
    
    @classmethod
    def parse_yaml(cls, yaml_content: str) -> DSLWorkflow:
        """解析YAML格式的工作流定义"""
        try:
            data = yaml.safe_load(yaml_content)
            return cls._convert_to_dsl_workflow(data)
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"YAML解析错误: {str(e)}")
        except Exception as e:
            raise ConfigValidationError(f"工作流定义解析失败: {str(e)}")
    
    @classmethod
    def parse_json(cls, json_content: str) -> DSLWorkflow:
        """解析JSON格式的工作流定义"""
        try:
            data = json.loads(json_content)
            return cls._convert_to_dsl_workflow(data)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"JSON解析错误: {str(e)}")
        except Exception as e:
            raise ConfigValidationError(f"工作流定义解析失败: {str(e)}")
    
    @classmethod
    def _convert_to_dsl_workflow(cls, data: Dict[str, Any]) -> DSLWorkflow:
        """将原始数据转换为DSL工作流对象"""
        # 转换节点
        nodes_data = data.get('nodes', [])
        nodes = []
        
        for node_data in nodes_data:
            node = cls._convert_node(node_data)
            nodes.append(node)
        
        # 创建工作流对象
        workflow = DSLWorkflow(
            name=data.get('name', 'unnamed_workflow'),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            nodes=nodes,
            start_node=data.get('start_node'),
            end_nodes=data.get('end_nodes', []),
            variables=data.get('variables', {}),
            metadata=data.get('metadata', {})
        )
        
        return workflow
    
    @classmethod
    def _convert_node(cls, node_data: Dict[str, Any]) -> DSLNode:
        """转换单个节点数据"""
        node_type = DSLNodeType(node_data.get('type', 'mcp_tool'))
        
        node = DSLNode(
            type=node_type,
            name=node_data.get('name', 'unnamed_node'),
            description=node_data.get('description', ''),
            config=node_data.get('config', {}),
            inputs=node_data.get('inputs', {}),
            outputs=node_data.get('outputs', []),
            next_nodes=node_data.get('next_nodes', []),
            condition=node_data.get('condition'),
            retry_config=node_data.get('retry_config'),
            timeout=node_data.get('timeout', 300)
        )
        
        return node
    
    @classmethod
    def validate_workflow(cls, workflow: DSLWorkflow) -> bool:
        """验证工作流定义的完整性"""
        errors = []
        
        # 检查节点引用
        node_ids = {node.id for node in workflow.nodes}
        
        # 检查起始节点
        if workflow.start_node not in node_ids:
            errors.append(f"起始节点不存在: {workflow.start_node}")
        
        # 检查结束节点
        for end_node in workflow.end_nodes:
            if end_node not in node_ids:
                errors.append(f"结束节点不存在: {end_node}")
        
        # 检查节点间连接
        for node in workflow.nodes:
            for next_node_id in node.next_nodes:
                if next_node_id not in node_ids:
                    errors.append(f"节点 {node.name} 引用了不存在的下一节点: {next_node_id}")
        
        # 检查条件节点
        for node in workflow.nodes:
            if node.type == DSLNodeType.CONDITION and not node.condition:
                errors.append(f"条件节点 {node.name} 缺少条件配置")
        
        if errors:
            error_msg = "工作流验证失败:\n" + "\n".join(errors)
            raise ConfigValidationError(error_msg)
        
        return True


class WorkflowBuilder:
    """工作流构建器"""
    
    def __init__(self, name: str):
        self.workflow = DSLWorkflow(
            name=name,
            nodes=[],
            start_node="",
            end_nodes=[]
        )
        self.current_node_id = None
    
    def add_start_node(self, name: str, description: str = "") -> 'WorkflowBuilder':
        """添加起始节点"""
        node = DSLNode(
            type=DSLNodeType.START,
            name=name,
            description=description
        )
        self.workflow.nodes.append(node)
        self.workflow.start_node = node.id
        self.current_node_id = node.id
        return self
    
    def add_mcp_tool_node(
        self,
        name: str,
        server: str,
        tool: str,
        inputs: Dict[str, str] = None,
        outputs: List[str] = None,
        description: str = ""
    ) -> 'WorkflowBuilder':
        """添加MCP工具节点"""
        node = DSLNode(
            type=DSLNodeType.MCP_TOOL,
            name=name,
            description=description,
            config={
                "server": server,
                "tool": tool
            },
            inputs=inputs or {},
            outputs=outputs or []
        )
        
        self.workflow.nodes.append(node)
        
        # 连接前一个节点
        if self.current_node_id:
            prev_node = self._find_node(self.current_node_id)
            if prev_node:
                prev_node.next_nodes.append(node.id)
        
        self.current_node_id = node.id
        return self
    
    def add_condition_node(
        self,
        name: str,
        condition: Dict[str, Any],
        description: str = ""
    ) -> 'WorkflowBuilder':
        """添加条件节点"""
        node = DSLNode(
            type=DSLNodeType.CONDITION,
            name=name,
            description=description,
            condition=condition
        )
        
        self.workflow.nodes.append(node)
        
        if self.current_node_id:
            prev_node = self._find_node(self.current_node_id)
            if prev_node:
                prev_node.next_nodes.append(node.id)
        
        self.current_node_id = node.id
        return self
    
    def add_transform_node(
        self,
        name: str,
        transform_script: str,
        inputs: Dict[str, str] = None,
        outputs: List[str] = None,
        description: str = ""
    ) -> 'WorkflowBuilder':
        """添加数据转换节点"""
        node = DSLNode(
            type=DSLNodeType.TRANSFORM,
            name=name,
            description=description,
            config={
                "script": transform_script
            },
            inputs=inputs or {},
            outputs=outputs or []
        )
        
        self.workflow.nodes.append(node)
        
        if self.current_node_id:
            prev_node = self._find_node(self.current_node_id)
            if prev_node:
                prev_node.next_nodes.append(node.id)
        
        self.current_node_id = node.id
        return self
    
    def add_end_node(self, name: str = "End", description: str = "") -> 'WorkflowBuilder':
        """添加结束节点"""
        node = DSLNode(
            type=DSLNodeType.END,
            name=name,
            description=description
        )
        
        self.workflow.nodes.append(node)
        self.workflow.end_nodes.append(node.id)
        
        if self.current_node_id:
            prev_node = self._find_node(self.current_node_id)
            if prev_node:
                prev_node.next_nodes.append(node.id)
        
        return self
    
    def set_variable(self, name: str, value: Any) -> 'WorkflowBuilder':
        """设置工作流变量"""
        self.workflow.variables[name] = value
        return self
    
    def build(self) -> DSLWorkflow:
        """构建工作流"""
        # 验证工作流
        WorkflowDSLParser.validate_workflow(self.workflow)
        return self.workflow
    
    def _find_node(self, node_id: str) -> Optional[DSLNode]:
        """查找节点"""
        for node in self.workflow.nodes:
            if node.id == node_id:
                return node
        return None


# 便捷函数
def create_commute_workflow() -> DSLWorkflow:
    """创建标准通勤工作流"""
    builder = WorkflowBuilder("Daily Commute Check")
    
    workflow = (builder
        .add_start_node("Start", "开始每日通勤检查")
        .add_mcp_tool_node(
            name="Calculate Route",
            server="amap-mcp-server",
            tool="calculate_route",
            inputs={
                "origin": "${variables.home_location}",
                "destination": "${variables.work_location}"
            },
            outputs=["route_info"]
        )
        .add_mcp_tool_node(
            name="Get Traffic",
            server="amap-mcp-server", 
            tool="get_traffic_condition",
            inputs={
                "origin": "${variables.home_location}",
                "destination": "${variables.work_location}"
            },
            outputs=["traffic_info"]
        )
        .add_transform_node(
            name="Process Data",
            transform_script="""
            # 处理路线和交通数据
            duration = route_info.duration
            distance = route_info.distance
            traffic_status = traffic_info.congestion_level
            
            # 计算建议出发时间
            suggested_departure = current_time + buffer_time
            """,
            inputs={
                "route_info": "${Calculate Route.route_info}",
                "traffic_info": "${Get Traffic.traffic_info}"
            },
            outputs=["processed_data"]
        )
        .add_mcp_tool_node(
            name="Send Notification",
            server="dingtalk-mcp-server",
            tool="send_commute_notification",
            inputs={
                "departure_time": "${Process Data.processed_data.suggested_departure}",
                "duration_minutes": "${Process Data.processed_data.duration}",
                "distance_km": "${Process Data.processed_data.distance}"
            }
        )
        .add_end_node("Complete", "通勤检查完成"))
    
    # 设置变量
    (workflow
        .set_variable("home_location", "116.481485,39.990464")
        .set_variable("work_location", "116.481485,39.990464")
        .set_variable("buffer_time", 30))  # 30分钟缓冲时间
    
    return workflow.build()


def workflow_to_yaml(workflow: DSLWorkflow) -> str:
    """将工作流转换为YAML格式"""
    # 转换为字典
    workflow_dict = workflow.dict()
    
    # 简化输出
    simplified = {
        "name": workflow_dict["name"],
        "description": workflow_dict["description"],
        "version": workflow_dict["version"],
        "start_node": workflow_dict["start_node"],
        "end_nodes": workflow_dict["end_nodes"],
        "variables": workflow_dict["variables"],
        "nodes": []
    }
    
    # 转换节点
    for node_dict in workflow_dict["nodes"]:
        node_simplified = {
            "id": node_dict["id"],
            "type": node_dict["type"],
            "name": node_dict["name"],
            "description": node_dict["description"]
        }
        
        if node_dict["config"]:
            node_simplified["config"] = node_dict["config"]
        if node_dict["inputs"]:
            node_simplified["inputs"] = node_dict["inputs"]
        if node_dict["outputs"]:
            node_simplified["outputs"] = node_dict["outputs"]
        if node_dict["next_nodes"]:
            node_simplified["next_nodes"] = node_dict["next_nodes"]
        if node_dict["condition"]:
            node_simplified["condition"] = node_dict["condition"]
            
        simplified["nodes"].append(node_simplified)
    
    return yaml.dump(simplified, default_flow_style=False, allow_unicode=True)