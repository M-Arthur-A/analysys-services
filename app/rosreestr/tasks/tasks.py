from app.tasks.celery import celery

@celery.task
def monitoring(
):
    pass
