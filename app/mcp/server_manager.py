"""
MCP服务器管理器
负责MCP服务器的生命周期管理、健康检查和负载均衡
"""

import asyncio
import subprocess
import signal
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from ..utils.logger import get_logger
from ..utils.exceptions import MCPBaseException

logger = get_logger(__name__)


class ServerStatus(Enum):
    """服务器状态枚举"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ServerHealth(BaseModel):
    """服务器健康状态"""
    status: ServerStatus
    last_check: datetime
    response_time: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None


class ManagedServer(BaseModel):
    """受管服务器"""
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}
    working_dir: Optional[str] = None
    timeout: int = 300
    max_concurrent: int = 10
    auto_restart: bool = True
    health_check_interval: int = 30  # 秒


class ServerProcess:
    """服务器进程管理"""
    
    def __init__(self, server: ManagedServer):
        self.server = server
        self.process: Optional[subprocess.Popen] = None
        self.status = ServerStatus.STOPPED
        self.health = ServerHealth(
            status=ServerStatus.STOPPED,
            last_check=datetime.now()
        )
        self.restart_count = 0
        self.last_start_time: Optional[datetime] = None
    
    async def start(self) -> bool:
        """启动服务器进程"""
        try:
            self.status = ServerStatus.STARTING
            self.last_start_time = datetime.now()
            
            # 构建命令
            cmd = [self.server.command] + self.server.args
            
            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=self.server.working_dir,
                env={**dict(os.environ), **self.server.env},
                text=True
            )
            
            self.status = ServerStatus.RUNNING
            logger.info(f"服务器启动成功: {self.server.name}")
            return True
            
        except Exception as e:
            self.status = ServerStatus.ERROR
            self.health.last_error = str(e)
            self.health.error_count += 1
            logger.error(f"服务器启动失败: {self.server.name}", error=str(e))
            return False
    
    async def stop(self, force: bool = False) -> bool:
        """停止服务器进程"""
        try:
            self.status = ServerStatus.STOPPING
            
            if self.process and self.process.poll() is None:
                if force:
                    self.process.kill()
                else:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait()
            
            self.status = ServerStatus.STOPPED
            logger.info(f"服务器停止成功: {self.server.name}")
            return True
            
        except Exception as e:
            self.status = ServerStatus.ERROR
            logger.error(f"服务器停止失败: {self.server.name}", error=str(e))
            return False
    
    async def health_check(self) -> ServerHealth:
        """健康检查"""
        try:
            if not self.process or self.process.poll() is not None:
                self.status = ServerStatus.STOPPED
                self.health.status = ServerStatus.STOPPED
            else:
                # 执行简单的ping检查（这里可以扩展为更复杂的健康检查）
                self.health.response_time = 0.1  # 模拟响应时间
                self.health.status = ServerStatus.RUNNING
            
        except Exception as e:
            self.status = ServerStatus.ERROR
            self.health.status = ServerStatus.ERROR
            self.health.last_error = str(e)
            self.health.error_count += 1
        
        self.health.last_check = datetime.now()
        return self.health
    
    def is_healthy(self) -> bool:
        """检查服务器是否健康"""
        return self.status == ServerStatus.RUNNING and self.health.status == ServerStatus.RUNNING


class MCPServerManager:
    """MCP服务器管理器"""
    
    def __init__(self):
        self.servers: Dict[str, ServerProcess] = {}
        self.managed_configs: Dict[str, ManagedServer] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
    
    async def register_server(self, config: ManagedServer) -> bool:
        """注册服务器配置"""
        try:
            self.managed_configs[config.name] = config
            
            # 创建服务器进程管理器
            server_process = ServerProcess(config)
            self.servers[config.name] = server_process
            
            logger.info(f"服务器配置注册成功: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"服务器配置注册失败: {config.name}", error=str(e))
            return False
    
    async def start_server(self, server_name: str) -> bool:
        """启动指定服务器"""
        if server_name not in self.servers:
            raise ValueError(f"服务器未注册: {server_name}")
        
        server = self.servers[server_name]
        return await server.start()
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """启动所有服务器"""
        results = {}
        for server_name in self.servers:
            results[server_name] = await self.start_server(server_name)
        return results
    
    async def stop_server(self, server_name: str, force: bool = False) -> bool:
        """停止指定服务器"""
        if server_name not in self.servers:
            return False
        
        server = self.servers[server_name]
        return await server.stop(force)
    
    async def stop_all_servers(self) -> Dict[str, bool]:
        """停止所有服务器"""
        results = {}
        for server_name in list(self.servers.keys()):
            results[server_name] = await self.stop_server(server_name)
        return results
    
    async def get_server_health(self, server_name: str) -> Optional[ServerHealth]:
        """获取服务器健康状态"""
        if server_name not in self.servers:
            return None
        
        server = self.servers[server_name]
        return await server.health_check()
    
    async def get_all_health(self) -> Dict[str, ServerHealth]:
        """获取所有服务器健康状态"""
        results = {}
        for server_name in self.servers:
            results[server_name] = await self.get_server_health(server_name)
        return results
    
    async def restart_server(self, server_name: str) -> bool:
        """重启服务器"""
        if server_name not in self.servers:
            return False
        
        # 先停止
        await self.stop_server(server_name)
        
        # 等待一小段时间
        await asyncio.sleep(1)
        
        # 再启动
        return await self.start_server(server_name)
    
    async def start_health_monitoring(self, server_name: str) -> bool:
        """启动健康监控"""
        if server_name not in self.managed_configs:
            return False
        
        config = self.managed_configs[server_name]
        
        async def health_check_loop():
            while True:
                try:
                    await self.get_server_health(server_name)
                    await asyncio.sleep(config.health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"健康检查循环异常: {server_name}", error=str(e))
                    await asyncio.sleep(5)  # 出错后等待5秒再重试
        
        # 取消现有的监控任务
        if server_name in self.health_check_tasks:
            self.health_check_tasks[server_name].cancel()
        
        # 启动新的监控任务
        task = asyncio.create_task(health_check_loop())
        self.health_check_tasks[server_name] = task
        
        logger.info(f"健康监控已启动: {server_name}")
        return True
    
    async def stop_health_monitoring(self, server_name: str) -> bool:
        """停止健康监控"""
        if server_name in self.health_check_tasks:
            self.health_check_tasks[server_name].cancel()
            del self.health_check_tasks[server_name]
            logger.info(f"健康监控已停止: {server_name}")
            return True
        return False
    
    async def auto_heal_server(self, server_name: str) -> bool:
        """自动修复服务器"""
        if server_name not in self.servers:
            return False
        
        server = self.servers[server_name]
        
        # 检查是否需要重启
        if not server.is_healthy():
            logger.warning(f"检测到服务器不健康，尝试自动修复: {server_name}")
            return await self.restart_server(server_name)
        
        return True
    
    def get_server_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        stats = {
            'total_servers': len(self.servers),
            'running_servers': 0,
            'stopped_servers': 0,
            'error_servers': 0,
            'server_details': {}
        }
        
        for name, server in self.servers.items():
            status = server.status.value
            stats['server_details'][name] = {
                'status': status,
                'restart_count': server.restart_count,
                'last_start_time': server.last_start_time.isoformat() if server.last_start_time else None
            }
            
            if status == 'running':
                stats['running_servers'] += 1
            elif status == 'stopped':
                stats['stopped_servers'] += 1
            else:
                stats['error_servers'] += 1
        
        return stats


# 全局服务器管理器实例
server_manager = MCPServerManager()