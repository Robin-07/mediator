import asyncio

from celery import Celery

from mediator.core.config import settings
from mediator.services.async_handlers import (
    submit_replicate_job,
    process_replicate_job,
    process_replicate_job_result,
)

celery_app = Celery(
    "mediator",
    broker=settings.CELERY_BROKER_URL,
)

celery_app.conf.task_default_queue = "default"


@celery_app.task(
    bind=True,
    name="submit_replicate_job_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
)
def submit_replicate_job_task(self, job_id: int):
    """
    Celery task to process a media generation job.
    It wraps an async function into a sync context.
    """
    asyncio.run(submit_replicate_job(job_id))


@celery_app.task(
    bind=True,
    name="process_replicate_job_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
)
def process_replicate_job_task(self, prediction_id: str, webhook_url: str):
    """
    Celery task to mock a replicate API request completion.
    It wraps an async function into a sync context.
    """
    asyncio.run(process_replicate_job(prediction_id, webhook_url))


@celery_app.task(
    bind=True,
    name="process_replicate_job_result_task",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
)
def process_replicate_job_result_task(self, prediction_id: str, media_url: str):
    """
    Celery task to mock a replicate API request completion.
    It wraps an async function into a sync context.
    """
    asyncio.run(process_replicate_job_result(prediction_id, media_url))
