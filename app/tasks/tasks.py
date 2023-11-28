from datetime import datetime
import os
import asyncio
import functools

from celery.schedules import crontab
from celery.utils.log import get_task_logger

from app.tasks.celery import celery
from app.rosreestr.utility import Utility as rr_utility
from app.fedresurs.utility import Utility as fr_utility
from app.config import settings



logger = get_task_logger(__name__)

celery.conf.beat_schedule = {
    'rr_check-every-two-min': {
        'task': 'tasks.tasks.rr_monitoring',
        'schedule': 120.0,
    },
    'rr_clear-folders-after-ten-days': {
        'task': 'tasks.tasks.folder_cleaning',
        'schedule': crontab(minute=0, hour=0),
        'args': (settings.RR_STORAGE, 10),
    },
    'fr_clear-folders-after-ten-days': {
        'task': 'tasks.tasks.folder_cleaning',
        'schedule': crontab(minute=0, hour=1),
        'args': (settings.FR_STORAGE, 10),
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
        # old files deletion
        for f in files:
            file_path = os.path.join(root,f)
            timestamp_of_file_modified = os.path.getmtime(file_path)
            modification_date = datetime.fromtimestamp(timestamp_of_file_modified)
            number_of_days = (datetime.now() - modification_date).days
            if number_of_days > days_expire:
                os.remove(file_path)
                logger.info(f" {days_expire} left, {f} has been deleted")
        # empty folder deletion
        deleted = set()
        still_has_subdirs = False
        for subdir in dirs:
            if os.path.join(root, subdir) not in deleted:
                still_has_subdirs = True
                break
        if not any(files) and not still_has_subdirs:
            os.rmdir(root)
            deleted.add(root)


@celery.task(name="fr_running")
def fr_run(uid: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fr_utility.scrap(uid))
