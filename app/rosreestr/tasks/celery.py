from celery import Celery

import sys
sys.path.append('./app')
from app.config import settings


celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER,
    include=["tasks.tasks"],
)
