from datetime import datetime
import os
import asyncio
import functools

from celery.schedules import crontab
from celery.utils.log import get_task_logger

from app.tasks.celery import celery
from app.rosreestr.utility import Utility as rr_utility



logger = get_task_logger(__name__)

celery.conf.beat_schedule = {
    'rr_check-every-two-min': {
        'task': 'tasks.tasks.rr_monitoring',
        'schedule': 120.0,
    },
    'clear_folders-after-ten-days': {
        'task': 'tasks.tasks.folder_cleaning',
        'schedule': crontab(minute=0, hour=0), # каждый день в полночь
        'args': ('/tmp/rosreestr', 10),
    },
}


def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))
    return wrapper


@celery.task(name="rr_quering")
def rr_adding(query_id: int | None = None):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rr_utility.query_orders(query_id))


@celery.task
def rr_monitoring():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rr_utility.check_orders())


@celery.task
def folder_cleaning(path: str, days_expire: int):
    for (root, dirs, files) in os.walk(path, topdown=True):
       for f in files:
           file_path = os.path.join(root,f)
           timestamp_of_file_modified = os.path.getmtime(file_path)
           modification_date = datetime.fromtimestamp(timestamp_of_file_modified)
           number_of_days = (datetime.now() - modification_date).days
           if number_of_days > days_expire:
               os.remove(file_path)
               logger.info(f" {days_expire} left, {f} has been deleted")

