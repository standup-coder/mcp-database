"""
监控和告警系统
集成Prometheus指标收集、健康检查和告警通知
"""

import asyncio
import time
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from fastapi import FastAPI, Response

from app.config.settings import settings
from app.utils.logger import get_logger


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricData:
    """指标数据"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric: str
    threshold: float
    operator: str  # gt, lt, eq, ne
    level: AlertLevel
    duration: int  # 持续时间(秒)
    description: str


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.metrics = {}
        self.setup_prometheus_metrics()
    
    def setup_prometheus_metrics(self):
        """设置Prometheus指标"""
        # 应用指标
        self.app_requests_total = Counter(
            'app_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )
        
        self.app_request_duration = Histogram(
            'app_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        self.app_errors_total = Counter(
            'app_errors_total',
            'Total number of errors',
            ['error_type']
        )
        
        # 系统指标
        self.system_cpu_percent = Gauge(
            'system_cpu_percent',
            'CPU usage percentage'
        )
        
        self.system_memory_percent = Gauge(
            'system_memory_percent',
            'Memory usage percentage'
        )
        
        self.system_disk_percent = Gauge(
            'system_disk_percent',
            'Disk usage percentage'
        )
        
        # MCP指标
        self.mcp_server_up = Gauge(
            'mcp_server_up',
            'MCP server status (1=up, 0=down)',
            ['server_name']
        )
        
        self.mcp_requests_total = Counter(
            'mcp_requests_total',
            'Total number of MCP requests',
            ['server_name', 'tool_name']
        )
        
        self.mcp_request_duration = Histogram(
            'mcp_request_duration_seconds',
            'MCP request duration in seconds',
            ['server_name', 'tool_name']
        )
        
        # 工作流指标
        self.workflow_executions_total = Counter(
            'workflow_executions_total',
            'Total number of workflow executions',
            ['workflow_id', 'status']
        )
        
        self.workflow_duration = Histogram(
            'workflow_duration_seconds',
            'Workflow execution duration in seconds',
            ['workflow_id']
        )
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_percent.set(cpu_percent)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self.system_memory_percent.set(memory.percent)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_percent.set(disk_percent)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk_percent,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
            return {}
    
    async def collect_app_metrics(self) -> Dict[str, Any]:
        """收集应用指标"""
        try:
            # 进程信息
            process = psutil.Process()
            
            return {
                'process_memory_mb': round(process.memory_info().rss / (1024**2), 2),
                'process_cpu_percent': process.cpu_percent(),
                'thread_count': process.num_threads(),
                'open_files': len(process.open_files()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"收集应用指标失败: {e}")
            return {}


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Dict] = {}
        self.notification_channels: List[str] = []
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """设置默认告警规则"""
        rules = [
            AlertRule(
                name="high_cpu_usage",
                metric="system_cpu_percent",
                threshold=80.0,
                operator="gt",
                level=AlertLevel.WARNING,
                duration=300,  # 5分钟
                description="CPU使用率超过80%"
            ),
            AlertRule(
                name="high_memory_usage",
                metric="system_memory_percent",
                threshold=85.0,
                operator="gt",
                level=AlertLevel.WARNING,
                duration=300,
                description="内存使用率超过85%"
            ),
            AlertRule(
                name="disk_space_low",
                metric="system_disk_percent",
                threshold=90.0,
                operator="gt",
                level=AlertLevel.ERROR,
                duration=600,  # 10分钟
                description="磁盘使用率超过90%"
            ),
            AlertRule(
                name="mcp_server_down",
                metric="mcp_server_up",
                threshold=1.0,
                operator="lt",
                level=AlertLevel.CRITICAL,
                duration=120,  # 2分钟
                description="MCP服务器不可用"
            )
        ]
        
        self.alert_rules.extend(rules)
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules.append(rule)
        self.logger.info(f"添加告警规则: {rule.name}")
    
    async def evaluate_rules(self, metrics: Dict[str, Any]):
        """评估告警规则"""
        for rule in self.alert_rules:
            if rule.metric in metrics:
                current_value = metrics[rule.metric]
                should_alert = self._evaluate_condition(current_value, rule.threshold, rule.operator)
                
                if should_alert:
                    await self.trigger_alert(rule, current_value, metrics)
                else:
                    await self.resolve_alert(rule.name)
    
    def _evaluate_condition(self, current_value: float, threshold: float, operator: str) -> bool:
        """评估告警条件"""
        if operator == "gt":
            return current_value > threshold
        elif operator == "lt":
            return current_value < threshold
        elif operator == "eq":
            return current_value == threshold
        elif operator == "ne":
            return current_value != threshold
        return False
    
    async def trigger_alert(self, rule: AlertRule, current_value: float, metrics: Dict[str, Any]):
        """触发告警"""
        alert_key = f"{rule.name}_{rule.metric}"
        
        if alert_key not in self.active_alerts:
            # 新告警
            alert_data = {
                'rule_name': rule.name,
                'metric': rule.metric,
                'current_value': current_value,
                'threshold': rule.threshold,
                'level': rule.level.value,
                'description': rule.description,
                'first_triggered': datetime.now(),
                'last_updated': datetime.now(),
                'metrics': metrics
            }
            
            self.active_alerts[alert_key] = alert_data
            await self.send_notifications(alert_data)
            self.logger.warning(f"触发告警: {rule.name} - {current_value}")
    
    async def resolve_alert(self, alert_name: str):
        """解决告警"""
        resolved_alerts = []
        for alert_key, alert_data in self.active_alerts.items():
            if alert_data['rule_name'] == alert_name:
                resolved_alerts.append(alert_key)
                self.logger.info(f"解决告警: {alert_name}")
        
        for alert_key in resolved_alerts:
            del self.active_alerts[alert_key]
    
    async def send_notifications(self, alert_data: Dict[str, Any]):
        """发送告警通知"""
        # 这里可以集成多种通知渠道
        notification_methods = [
            self._send_dingtalk_notification,
            self._send_log_notification
        ]
        
        for method in notification_methods:
            try:
                await method(alert_data)
            except Exception as e:
                self.logger.error(f"发送通知失败: {e}")
    
    async def _send_dingtalk_notification(self, alert_data: Dict[str, Any]):
        """发送钉钉告警通知"""
        try:
            from app.mcp.servers.dingtalk_server import DingTalkMCPServer
            
            message = f"""
🚨 告警通知

告警名称: {alert_data['rule_name']}
级别: {alert_data['level'].upper()}
描述: {alert_data['description']}
当前值: {alert_data['current_value']}
阈值: {alert_data['threshold']}
触发时间: {alert_data['first_triggered'].strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            server = DingTalkMCPServer()
            await server.send_message(message)
            
        except Exception as e:
            self.logger.error(f"发送钉钉通知失败: {e}")
    
    async def _send_log_notification(self, alert_data: Dict[str, Any]):
        """发送日志告警通知"""
        self.logger.error(f"告警详情: {json.dumps(alert_data, indent=2, default=str)}")


class MonitoringSystem:
    """监控系统主类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.is_running = False
        self.collection_interval = 60  # 60秒收集一次
        
    async def start_monitoring(self):
        """启动监控"""
        self.is_running = True
        self.logger.info("启动监控系统")
        
        while self.is_running:
            try:
                # 收集指标
                system_metrics = await self.metrics_collector.collect_system_metrics()
                app_metrics = await self.metrics_collector.collect_app_metrics()
                
                all_metrics = {**system_metrics, **app_metrics}
                
                # 评估告警规则
                await self.alert_manager.evaluate_rules(all_metrics)
                
                # 等待下次收集
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
                await asyncio.sleep(30)  # 异常后等待30秒重试
    
    async def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        self.logger.info("停止监控系统")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        return list(self.alert_manager.active_alerts.values())
    
    def get_metrics_endpoint(self) -> bytes:
        """获取Prometheus指标端点数据"""
        return generate_latest()


# 全局监控实例
monitoring_system = MonitoringSystem()


def setup_monitoring_routes(app: FastAPI):
    """设置监控路由"""
    
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus指标端点"""
        return Response(
            content=monitoring_system.get_metrics_endpoint(),
            media_type="text/plain"
        )
    
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        try:
            system_metrics = await monitoring_system.metrics_collector.collect_system_metrics()
            
            health_status = "healthy"
            if system_metrics.get('cpu_percent', 0) > 90:
                health_status = "degraded"
            elif system_metrics.get('memory_percent', 0) > 95:
                health_status = "degraded"
            
            return {
                "status": health_status,
                "timestamp": datetime.now().isoformat(),
                "system_metrics": system_metrics,
                "active_alerts": len(monitoring_system.get_active_alerts())
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @app.get("/alerts")
    async def get_alerts():
        """获取当前告警"""
        return {
            "active_alerts": monitoring_system.get_active_alerts(),
            "timestamp": datetime.now().isoformat()
        }


# 请求中间件用于收集HTTP指标
async def metrics_middleware(request, call_next):
    """请求指标收集中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # 记录请求指标
    method = request.method
    endpoint = request.url.path
    status = response.status_code
    
    # 更新Prometheus指标
    monitoring_system.metrics_collector.app_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status)
    ).inc()
    
    duration = time.time() - start_time
    monitoring_system.metrics_collector.app_request_duration.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)
    
    return response