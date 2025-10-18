"""
Celery Application Configuration
backend/celery_app.py

Configures Celery for distributed task processing of academic papers.
"""

from celery import Celery
import os

# Initialize Celery app
celery_app = Celery(
    'academic_integrity',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # 9 minutes soft limit

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster'
    },

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,

    # Task routing
    task_default_queue='default',
    task_queues={
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'ml_processing': {
            'exchange': 'ml_processing',
            'routing_key': 'ml.process',
        },
    },

    # Beat schedule (for periodic tasks)
    beat_schedule={
        'cleanup-old-jobs': {
            'task': 'celery_tasks.cleanup_old_jobs',
            'schedule': 3600.0,  # Every hour
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['celery_tasks'])

if __name__ == '__main__':
    celery_app.start()
