#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统健康检查脚本
定期检查系统各组件的运行状态
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Any

# 添加项目路径
sys.path.append('.')

from app.config.settings import settings
from app.utils.logger import get_logger
from app.mcp.server_manager import server_manager
from app.mcp.orchestrator import mcp_orchestrator


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.check_results = []
    
    async def check_all_components(self) -> Dict[str, Any]:
        """检查所有系统组件"""
        self.logger.info("开始系统健康检查")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'components': {}
        }
        
        # 并行执行各项检查
        check_tasks = [
            self.check_configuration(),
            self.check_dependencies(),
            self.check_mcp_servers(),
            self.check_network_connectivity(),
            self.check_disk_space(),
            self.check_memory_usage()
        ]
        
        component_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # 处理检查结果
        component_names = [
            'configuration', 'dependencies', 'mcp_servers', 
            'network', 'disk_space', 'memory'
        ]
        
        for name, result in zip(component_names, component_results):
            if isinstance(result, Exception):
                results['components'][name] = {
                    'status': 'error',
                    'error': str(result)
                }
            else:
                results['components'][name] = result
        
        # 计算总体状态
        results['overall_status'] = self._calculate_overall_status(results['components'])
        
        self.logger.info(f"健康检查完成，总体状态: {results['overall_status']}")
        return results
    
    async def check_configuration(self) -> Dict[str, Any]:
        """检查配置"""
        try:
            # 检查必需配置项
            required_configs = [
                'AMAP_API_KEY',
                'AMAP_ORIGIN',
                'AMAP_DESTINATION', 
                'DINGTALK_WEBHOOK_URL',
                'DINGTALK_SECRET'
            ]
            
            missing_configs = []
            invalid_configs = []
            
            for config_name in required_configs:
                config_value = getattr(settings, config_name.lower(), None)
                if not config_value or 'your_' in str(config_value).lower():
                    missing_configs.append(config_name)
            
            # 验证坐标格式
            try:
                from app.config.validators import validate_coordinates
                validate_coordinates(settings.amap_origin)
                validate_coordinates(settings.amap_destination)
            except Exception:
                invalid_configs.append('坐标格式')
            
            status = 'healthy' if not (missing_configs or invalid_configs) else 'degraded'
            
            return {
                'status': status,
                'missing_configs': missing_configs,
                'invalid_configs': invalid_configs,
                'total_required': len(required_configs)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖包"""
        try:
            import pkg_resources
            
            # 检查核心依赖
            required_packages = [
                'fastapi', 'uvicorn', 'celery', 'redis',
                'httpx', 'requests', 'pydantic', 'loguru'
            ]
            
            missing_packages = []
            version_issues = []
            
            for package in required_packages:
                try:
                    dist = pkg_resources.get_distribution(package)
                    # 可以添加版本检查逻辑
                except pkg_resources.DistributionNotFound:
                    missing_packages.append(package)
            
            status = 'healthy' if not missing_packages else 'degraded'
            
            return {
                'status': status,
                'missing_packages': missing_packages,
                'version_issues': version_issues
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_mcp_servers(self) -> Dict[str, Any]:
        """检查MCP服务器状态"""
        try:
            # 获取所有服务器健康状态
            health_status = await server_manager.get_all_health()
            
            running_count = sum(1 for health in health_status.values() 
                              if health and health.status.name == 'RUNNING')
            total_count = len(health_status)
            
            status = 'healthy' if running_count == total_count else 'degraded'
            
            return {
                'status': status,
                'running_servers': running_count,
                'total_servers': total_count,
                'details': {name: health.dict() if health else None 
                           for name, health in health_status.items()}
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_network_connectivity(self) -> Dict[str, Any]:
        """检查网络连接"""
        try:
            import httpx
            
            # 测试关键服务连接
            test_urls = [
                ('高德API', 'https://restapi.amap.com'),
                ('钉钉API', 'https://oapi.dingtalk.com'),
                ('Redis', f'redis://{settings.redis_host}:{settings.redis_port}')
            ]
            
            connectivity_results = {}
            failed_connections = []
            
            for service_name, url in test_urls:
                try:
                    if url.startswith('http'):
                        async with httpx.AsyncClient() as client:
                            response = await client.get(url, timeout=5)
                            connectivity_results[service_name] = response.status_code == 200
                    else:
                        # Redis连接测试
                        import redis
                        r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
                        connectivity_results[service_name] = r.ping()
                        
                except Exception:
                    connectivity_results[service_name] = False
                    failed_connections.append(service_name)
            
            status = 'healthy' if not failed_connections else 'degraded'
            
            return {
                'status': status,
                'connectivity': connectivity_results,
                'failed_connections': failed_connections
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            import shutil
            
            # 检查关键目录
            directories = ['.', './logs', './data']
            space_info = {}
            
            low_space_dirs = []
            
            for directory in directories:
                try:
                    total, used, free = shutil.disk_usage(directory)
                    free_gb = free / (1024**3)
                    used_percent = (used / total) * 100
                    
                    space_info[directory] = {
                        'free_gb': round(free_gb, 2),
                        'used_percent': round(used_percent, 1)
                    }
                    
                    if free_gb < 1:  # 少于1GB警告
                        low_space_dirs.append(directory)
                        
                except Exception:
                    space_info[directory] = {'error': '无法获取空间信息'}
            
            status = 'healthy' if not low_space_dirs else 'warning'
            
            return {
                'status': status,
                'space_info': space_info,
                'low_space_directories': low_space_dirs
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_memory_usage(self) -> Dict[str, Any]:
        """检查内存使用"""
        try:
            import psutil
            
            # 获取系统内存信息
            memory = psutil.virtual_memory()
            
            memory_info = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_percent': memory.percent,
                'free_gb': round(memory.free / (1024**3), 2)
            }
            
            # 检查Python进程内存
            process = psutil.Process()
            process_memory_mb = round(process.memory_info().rss / (1024**2), 2)
            
            status = 'healthy'
            warnings = []
            
            if memory.percent > 90:
                status = 'warning'
                warnings.append('系统内存使用率过高')
            
            if process_memory_mb > 500:  # 500MB警告
                status = 'warning' if status == 'healthy' else status
                warnings.append('Python进程内存使用过高')
            
            return {
                'status': status,
                'system_memory': memory_info,
                'process_memory_mb': process_memory_mb,
                'warnings': warnings
            }
            
        except ImportError:
            return {
                'status': 'warning',
                'error': 'psutil未安装，无法检查内存使用'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_overall_status(self, components: Dict[str, Any]) -> str:
        """计算总体健康状态"""
        statuses = [component.get('status', 'unknown') 
                   for component in components.values()]
        
        if 'error' in statuses:
            return 'unhealthy'
        elif 'degraded' in statuses or 'warning' in statuses:
            return 'degraded'
        elif all(status == 'healthy' for status in statuses):
            return 'healthy'
        else:
            return 'unknown'
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成健康检查报告"""
        report = []
        report.append("=" * 50)
        report.append("系统健康检查报告")
        report.append("=" * 50)
        report.append(f"检查时间: {results['timestamp']}")
        report.append(f"总体状态: {results['overall_status'].upper()}")
        report.append("")
        
        for component_name, component_result in results['components'].items():
            status = component_result.get('status', 'UNKNOWN')
            status_icon = {
                'healthy': '✅',
                'degraded': '⚠️',
                'warning': '⚠️',
                'error': '❌',
                'unknown': '❓'
            }.get(status, '❓')
            
            report.append(f"{status_icon} {component_name.upper()}: {status.upper()}")
            
            # 添加详细信息
            if status in ['degraded', 'warning', 'error']:
                if 'missing_configs' in component_result:
                    report.append(f"   缺失配置: {', '.join(component_result['missing_configs'])}")
                if 'failed_connections' in component_result:
                    report.append(f"   连接失败: {', '.join(component_result['failed_connections'])}")
                if 'error' in component_result:
                    report.append(f"   错误信息: {component_result['error']}")
            report.append("")
        
        return "\n".join(report)


async def main():
    """主函数"""
    checker = HealthChecker()
    results = await checker.check_all_components()
    report = checker.generate_report(results)
    print(report)
    
    # 根据总体状态决定退出码
    if results['overall_status'] == 'healthy':
        sys.exit(0)
    elif results['overall_status'] == 'degraded':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())