import asyncio
import io
import logging
from datetime import datetime

import boto3
import httpx

from mediator.core.config import settings
from mediator.core.db import async_session_maker
from mediator.crud.job import get_job, get_job_by_prediction_id, update_job_result
from mediator.models.job import Job

logger = logging.getLogger(__name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

# ----------------------- Mediator task handlers -----------------------


async def submit_replicate_job(job_id: int):
    """
    Call Replicate API (Async/Mocked) to submit the job, update prediction ID and other job details in DB.
    """
    async with async_session_maker() as db:
        job: Job = await get_job(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            job.retry_attempts += 1
            job.updated_at = datetime.utcnow()
            await db.commit()
            headers = {
                "Content-Type": "application/json",
            }
            payload = {
                "version": settings.REPLICATE_MODEL_VERSION,
                "input": job.parameters,
                "webhook": settings.REPLICATE_CALLBACK_URL,
                "webhook_events_filter": [""],
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.REPLICATE_PREDICTIONS_MOCK_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                prediction_id = response.json()["id"]

            await update_job_result(
                db, job, status="processing", prediction_id=prediction_id
            )
            logger.info(
                f"Job {job_id} processing started. Prediction ID: {prediction_id}"
            )

        except Exception as e:
            await update_job_result(db, job, status="failed")
            logger.exception(f"Job {job_id} failed: {str(e)}")


async def process_replicate_job_result(prediction_id: str, media_url: str):
    """
    Fetch the generated media, upload to S3 and update job status in DB.
    """
    async with async_session_maker() as db:
        job = await get_job_by_prediction_id(db, prediction_id)
        if not job:
            logger.error(f"No job found for prediction ID: {prediction_id}")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(media_url)
                response.raise_for_status()
                content = response.content

            filename = f"job-{job.id}_{prediction_id}.jpg"

            s3.upload_fileobj(
                Fileobj=io.BytesIO(content),
                Bucket=settings.S3_BUCKET_NAME,
                Key=filename,
                ExtraArgs={"ContentType": "image/jpg"},
            )

            s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"

            await update_job_result(db, job, status="completed", media_url=s3_url)
            logger.info(f"Job {job.id} updated with media at {s3_url}")

        except Exception as e:
            await update_job_result(db, job, status="failed")
            logger.exception(f"Failed to handle callback for job {job.id}: {e}")


# ----------------------- Mocked Replicate handlers -----------------------


async def process_replicate_job(prediction_id: str, webhook_url: str):
    """
    Simulate job processing latency by sleeping, then invoke the `webhook_url` provided by the API Client.
    """
    await asyncio.sleep(5)

    media_url = settings.DUMMY_IMAGE_URL
    webhook_payload = {
        "id": prediction_id,
        "status": "completed",
        "output": [media_url],
        "completed_at": datetime.now().isoformat(),
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(webhook_url, json=webhook_payload)
            logger.info(f"Sent webhook to {webhook_url}: status={resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
