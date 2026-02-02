"""
性能监控和指标收集增强
提供更详细的性能分析和优化建议
"""

import asyncio
import time
import psutil
import tracemalloc
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
import statistics

from app.utils.logger import get_logger


@dataclass
class PerformanceSnapshot:
    """性能快照"""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: int
    network_bytes_recv: int
    thread_count: int
    open_files: int


@dataclass
class PerformanceAnalysis:
    """性能分析结果"""
    period: str  # '1min', '5min', '15min', '1hour'
    avg_cpu: float
    max_cpu: float
    avg_memory_mb: float
    max_memory_mb: float
    io_read_mb: float
    io_write_mb: float
    recommendations: List[str]


class AdvancedPerformanceMonitor:
    """高级性能监控器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.snapshots: Dict[str, deque] = {
            '1min': deque(maxlen=60),    # 1分钟内每秒一个快照
            '5min': deque(maxlen=300),   # 5分钟内每秒一个快照
            '15min': deque(maxlen=900),  # 15分钟内每秒一个快照
            '1hour': deque(maxlen=3600)  # 1小时内每秒一个快照
        }
        
        self.baseline_metrics: Dict[str, Any] = {}
        self.performance_thresholds: Dict[str, float] = {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'disk_io_warning': 100.0,  # MB/s
            'network_warning': 1000000  # bytes/s
        }
        
        self.is_monitoring = False
        self.monitoring_task = None
        
    async def start_monitoring(self, interval: float = 1.0):
        """开始性能监控"""
        self.is_monitoring = True
        self.logger.info(f"开始性能监控，采样间隔: {interval}秒")
        
        # 初始化基准线
        await self._establish_baseline()
        
        # 启动监控任务
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
    
    async def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("性能监控已停止")
    
    async def _monitoring_loop(self, interval: float):
        """监控循环"""
        last_snapshot = None
        
        while self.is_monitoring:
            try:
                # 获取当前快照
                current_snapshot = await self._collect_snapshot()
                
                # 计算IO差异（相对于上次快照）
                if last_snapshot:
                    await self._calculate_io_diff(current_snapshot, last_snapshot)
                
                # 存储快照
                self._store_snapshot(current_snapshot)
                
                # 分析性能趋势
                await self._analyze_performance_trends(current_snapshot)
                
                last_snapshot = current_snapshot
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"性能监控异常: {e}")
                await asyncio.sleep(5)
    
    async def _collect_snapshot(self) -> PerformanceSnapshot:
        """收集性能快照"""
        timestamp = datetime.now()
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # 磁盘IO
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # 网络IO
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent if net_io else 0
        bytes_recv = net_io.bytes_recv if net_io else 0
        
        return PerformanceSnapshot(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_mb=process_memory.rss / (1024 * 1024),
            memory_percent=memory.percent,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_bytes_sent=bytes_sent,
            network_bytes_recv=bytes_recv,
            thread_count=process.num_threads(),
            open_files=len(process.open_files()) if hasattr(process, 'open_files') else 0
        )
    
    async def _calculate_io_diff(self, current: PerformanceSnapshot, last: PerformanceSnapshot):
        """计算IO差异"""
        time_diff = (current.timestamp - last.timestamp).total_seconds()
        if time_diff > 0:
            current.disk_io_read_mb = (current.disk_io_read_mb - last.disk_io_read_mb) / time_diff
            current.disk_io_write_mb = (current.disk_io_write_mb - last.disk_io_write_mb) / time_diff
            current.network_bytes_sent = (current.network_bytes_sent - last.network_bytes_sent) / time_diff
            current.network_bytes_recv = (current.network_bytes_recv - last.network_bytes_recv) / time_diff
    
    def _store_snapshot(self, snapshot: PerformanceSnapshot):
        """存储快照到各个时间窗口"""
        for period, queue in self.snapshots.items():
            queue.append(snapshot)
    
    async def _establish_baseline(self):
        """建立性能基准线"""
        self.logger.info("正在建立性能基准线...")
        
        baseline_snapshots = []
        for _ in range(60):  # 收集1分钟的数据
            snapshot = await self._collect_snapshot()
            baseline_snapshots.append(snapshot)
            await asyncio.sleep(1)
        
        # 计算基准值
        self.baseline_metrics = {
            'avg_cpu': statistics.mean(s.cpu_percent for s in baseline_snapshots),
            'avg_memory_mb': statistics.mean(s.memory_mb for s in baseline_snapshots),
            'avg_thread_count': statistics.mean(s.thread_count for s in baseline_snapshots),
            'baseline_timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"基准线建立完成: CPU={self.baseline_metrics['avg_cpu']:.1f}%")
    
    async def _analyze_performance_trends(self, current_snapshot: PerformanceSnapshot):
        """分析性能趋势"""
        # 检查是否超出阈值
        alerts = []
        
        if current_snapshot.cpu_percent > self.performance_thresholds['cpu_critical']:
            alerts.append(f"CPU使用率过高: {current_snapshot.cpu_percent:.1f}%")
        
        if current_snapshot.memory_percent > self.performance_thresholds['memory_critical']:
            alerts.append(f"内存使用率过高: {current_snapshot.memory_percent:.1f}%")
        
        if current_snapshot.disk_io_read_mb > self.performance_thresholds['disk_io_warning']:
            alerts.append(f"磁盘读取IO过高: {current_snapshot.disk_io_read_mb:.1f} MB/s")
        
        if alerts:
            self.logger.warning("性能告警: " + "; ".join(alerts))
    
    def get_analysis(self, period: str = '5min') -> Optional[PerformanceAnalysis]:
        """获取指定时间段的性能分析"""
        if period not in self.snapshots:
            return None
        
        snapshots = list(self.snapshots[period])
        if not snapshots:
            return None
        
        # 计算统计值
        cpu_values = [s.cpu_percent for s in snapshots]
        memory_values = [s.memory_mb for s in snapshots]
        io_read_values = [s.disk_io_read_mb for s in snapshots]
        io_write_values = [s.disk_io_write_mb for s in snapshots]
        
        analysis = PerformanceAnalysis(
            period=period,
            avg_cpu=statistics.mean(cpu_values),
            max_cpu=max(cpu_values),
            avg_memory_mb=statistics.mean(memory_values),
            max_memory_mb=max(memory_values),
            io_read_mb=sum(io_read_values),
            io_write_mb=sum(io_write_values),
            recommendations=self._generate_recommendations(snapshots)
        )
        
        return analysis
    
    def _generate_recommendations(self, snapshots: List[PerformanceSnapshot]) -> List[str]:
        """生成性能优化建议"""
        recommendations = []
        
        if not snapshots:
            return recommendations
        
        # CPU使用率分析
        avg_cpu = statistics.mean(s.cpu_percent for s in snapshots)
        if avg_cpu > self.performance_thresholds['cpu_warning']:
            recommendations.append("考虑优化CPU密集型操作或增加CPU资源")
        
        # 内存使用分析
        avg_memory = statistics.mean(s.memory_mb for s in snapshots)
        max_memory = max(s.memory_mb for s in snapshots)
        if max_memory > avg_memory * 2:
            recommendations.append("存在内存使用峰值，考虑内存泄漏检查")
        
        # IO分析
        avg_io_read = statistics.mean(s.disk_io_read_mb for s in snapshots)
        avg_io_write = statistics.mean(s.disk_io_write_mb for s in snapshots)
        if avg_io_read > self.performance_thresholds['disk_io_warning']:
            recommendations.append("磁盘读取IO较高，考虑使用缓存或SSD")
        if avg_io_write > self.performance_thresholds['disk_io_warning']:
            recommendations.append("磁盘写入IO较高，考虑批量写入优化")
        
        # 线程分析
        avg_threads = statistics.mean(s.thread_count for s in snapshots)
        if avg_threads > 50:
            recommendations.append("线程数量较多，考虑线程池优化")
        
        return recommendations
    
    def get_current_performance(self) -> Dict[str, Any]:
        """获取当前性能状态"""
        try:
            snapshot = asyncio.run(self._collect_snapshot())
            
            return {
                'timestamp': snapshot.timestamp.isoformat(),
                'cpu_percent': snapshot.cpu_percent,
                'memory_mb': snapshot.memory_mb,
                'memory_percent': snapshot.memory_percent,
                'disk_io_read_mb': snapshot.disk_io_read_mb,
                'disk_io_write_mb': snapshot.disk_io_write_mb,
                'network_bytes_sent': snapshot.network_bytes_sent,
                'network_bytes_recv': snapshot.network_bytes_recv,
                'thread_count': snapshot.thread_count,
                'open_files': snapshot.open_files,
                'status': self._get_performance_status(snapshot)
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_performance_status(self, snapshot: PerformanceSnapshot) -> str:
        """获取性能状态"""
        if (snapshot.cpu_percent > self.performance_thresholds['cpu_critical'] or
            snapshot.memory_percent > self.performance_thresholds['memory_critical']):
            return 'critical'
        elif (snapshot.cpu_percent > self.performance_thresholds['cpu_warning'] or
              snapshot.memory_percent > self.performance_thresholds['memory_warning']):
            return 'warning'
        else:
            return 'normal'


class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.tracking_enabled = False
    
    def start_tracking(self):
        """开始内存跟踪"""
        if not self.tracking_enabled:
            tracemalloc.start()
            self.tracking_enabled = True
            self.logger.info("内存跟踪已启动")
    
    def stop_tracking(self):
        """停止内存跟踪"""
        if self.tracking_enabled:
            tracemalloc.stop()
            self.tracking_enabled = False
            self.logger.info("内存跟踪已停止")
    
    def get_top_memory_consumers(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取内存消耗最多的对象"""
        if not self.tracking_enabled:
            return []
        
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            results = []
            for stat in top_stats[:limit]:
                results.append((
                    f"{stat.traceback.format()[0]}",
                    stat.size_diff
                ))
            
            return results
        except Exception as e:
            self.logger.error(f"获取内存统计失败: {e}")
            return []


# 全局实例
performance_monitor = AdvancedPerformanceMonitor()
memory_profiler = MemoryProfiler()


def get_performance_dashboard() -> Dict[str, Any]:
    """获取性能仪表板数据"""
    dashboard = {
        'timestamp': datetime.now().isoformat(),
        'current': performance_monitor.get_current_performance(),
        'analyses': {}
    }
    
    # 获取各时间段分析
    for period in ['1min', '5min', '15min']:
        analysis = performance_monitor.get_analysis(period)
        if analysis:
            dashboard['analyses'][period] = {
                'avg_cpu': analysis.avg_cpu,
                'max_cpu': analysis.max_cpu,
                'avg_memory_mb': analysis.avg_memory_mb,
                'max_memory_mb': analysis.max_memory_mb,
                'recommendations': analysis.recommendations
            }
    
    # 获取内存分析
    memory_profiler.start_tracking()
    top_consumers = memory_profiler.get_top_memory_consumers(5)
    memory_profiler.stop_tracking()
    
    dashboard['memory_analysis'] = {
        'top_consumers': top_consumers
    }
    
    return dashboard