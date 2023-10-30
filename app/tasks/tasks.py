import asyncio

from celery.schedules import crontab
from celery.utils.log import get_task_logger

from app.tasks.celery import celery
from app.rosreestr.utility import Utility as rr_utility



logger = get_task_logger(__name__)


celery.conf.beat_schedule = {
    'rr_check-every-two-min': {
        'task': 'tasks.tasks.rr_monitoring',
        'schedule': 10.0,
        # 'args': (16, 16)
    },
}

@celery.task
def rr_monitoring():
    # сделать, чтобы проставлялся is_ready после скачки всех ордеров
    asyncio.run(rr_utility.check_orders())
    print(123)
    logger.info("123")

# чистка временных файлов
