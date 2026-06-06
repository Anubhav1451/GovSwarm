from celery import Celery
from app.core.config import settings

# Initialize Celery application with Redis broker and backend
celery_app = Celery(
    "govswarm_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.workers.compliance_worker"]
)

# Configure Celery with JSON serialization and UTC timezone
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)
