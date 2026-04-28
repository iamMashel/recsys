from celery import Celery
from celery.schedules import crontab
from app.core.config import get_settings

settings = get_settings()

celery = Celery(
    "recsys",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.tasks"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery.conf.beat_schedule = {
    "sync-gorse-every-hour": {
        "task": "workers.tasks.sync_all_to_gorse",
        "schedule": crontab(minute=0),  # top of every hour
    },
    "index-embeddings-daily": {
        "task": "workers.tasks.index_all_embeddings",
        "schedule": crontab(hour=2, minute=0),  # 2am daily
    },
}
