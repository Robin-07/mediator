import asyncio
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import boto3
import httpx

from mediator.core.config import settings
from mediator.core.database import AsyncSessionLocal
from mediator.crud.job import get_job, update_job_result
from mediator.models.job import Job

logger = logging.getLogger(__name__)

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


async def process_generation_job(job_id: int):
    """
    Handles the image generation task. This function:
    - Fetches the job from DB
    - Calls Replicate API
    - Downloads and uploads image to S3
    - Updates job status, retry attempts, timestamps
    """
    async with AsyncSessionLocal() as db:
        job: Job = await get_job(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            job.retry_attempts += 1
            job.updated_at = datetime.utcnow()
            await db.commit()

            # --- Replicate API call ---
            headers = {
                "Authorization": f"Token {settings.REPLICATE_API_TOKEN}",
                "Content-Type": "application/json",
            }
            payload = {
                "version": settings.REPLICATE_MODEL_VERSION,
                "input": job.parameters,  # assuming this is a dict
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.REPLICATE_PREDICTIONS_API,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                prediction = response.json()
                image_url = prediction["output"][-1]  # get last output image

                # Download image
                image_resp = await client.get(image_url)
                image_resp.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(image_resp.content)
                tmp_path = tmp_file.name

            # --- Upload to S3 ---
            s3_key = f"generated/job-{job_id}.png"
            s3.upload_file(
                tmp_path,
                settings.S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={"ContentType": "image/png"},
            )

            os.remove(tmp_path)

            media_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

            await update_job_result(db, job, status="completed", media_url=media_url)
            logger.info(f"Job {job_id} completed and uploaded to {media_url}")

        except Exception as e:
            await update_job_result(db, job, status="failed")
            logger.exception(f"Job {job_id} failed: {str(e)}")


async def replicate_prediction_complete(prediction_id: str, webhook_url: str):
    await asyncio.sleep(5)  # Simulate delay

    result_url = f"https://placekitten.com/512/512?pred={prediction_id}"
    webhook_payload = {
        "id": prediction_id,
        "status": "completed",
        "output": [result_url],
        "completed_at": "2025-07-23T12:00:03Z",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(webhook_url, json=webhook_payload)
            logger.info(f"Webhook to {webhook_url} sent: status={resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
