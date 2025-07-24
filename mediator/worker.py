import asyncio

from celery import Celery

from mediator.core.config import settings
from mediator.services.job_handler import process_generation_job

celery_app = Celery(
    "mediator",
    broker=settings.CELERY_BROKER_URL,
)

celery_app.conf.task_routes = {"mediator.worker.generate_media_task": "default"}
celery_app.conf.task_default_queue = "default"


@celery_app.task(
    bind=True,
    name="generate_media_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
)
def generate_media_task(self, job_id: int):
    """
    Celery task to process a media generation job.
    It wraps an async function into a sync context.
    """
    asyncio.run(process_generation_job(job_id))
