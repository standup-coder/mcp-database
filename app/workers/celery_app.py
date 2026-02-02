"""
Celery应用配置
实现任务调度和工作流编排
"""

from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 创建Celery应用实例
celery_app = Celery('mcp_commute_assistant')

# 配置Celery
celery_app.conf.update(
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=settings.celery_accept_content,
    timezone=settings.celery_timezone,
    enable_utc=settings.celery_enable_utc,
    
    # 任务配置
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Worker配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # 结果配置
    result_expires=3600,  # 1小时后过期
    result_cache_max=1000,
    
    # 重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# 配置定时任务
celery_app.conf.beat_schedule = {
    # 每天早上通勤检查
    'daily-commute-check': {
        'task': 'app.workers.tasks.check_commute_and_notify',
        'schedule': crontab(
            minute=settings.commute_check_cron.split()[1],
            hour=settings.commute_check_cron.split()[2],
            day_of_week=settings.commute_check_cron.split()[5]
        ),
        'options': {
            'queue': 'commute_tasks'
        }
    },
    
    # 每小时健康检查
    'hourly-health-check': {
        'task': 'app.workers.tasks.health_check',
        'schedule': crontab(minute='0'),  # 每小时整点执行
        'options': {
            'queue': 'health_tasks'
        }
    },
    
    # 每天凌晨清理过期任务结果
    'daily-cleanup-results': {
        'task': 'app.workers.tasks.cleanup_expired_results',
        'schedule': crontab(hour='2', minute='0'),  # 凌晨2点执行
        'options': {
            'queue': 'maintenance_tasks'
        }
    }
}

# 队列路由配置
celery_app.conf.task_routes = {
    'app.workers.tasks.check_commute_and_notify': {'queue': 'commute_tasks'},
    'app.workers.tasks.health_check': {'queue': 'health_tasks'},
    'app.workers.tasks.cleanup_expired_results': {'queue': 'maintenance_tasks'},
    'app.workers.tasks.send_notification': {'queue': 'notification_tasks'},
    'app.workers.tasks.calculate_route': {'queue': 'calculation_tasks'},
}

# 任务超时配置
celery_app.conf.task_time_limit = 300  # 5分钟
celery_app.conf.task_soft_time_limit = 240  # 4分钟

logger.info("Celery应用配置完成")
logger.info(f"Broker URL: {settings.celery_broker_url}")
logger.info(f"时区设置: {settings.celery_timezone}")