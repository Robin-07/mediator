import os
import httpx
from pathlib import Path
from mediator.crud.job import get_job, update_job_result
from mediator.core.database import AsyncSessionLocal
from mediator.models.job import Job
import logging

logger = logging.getLogger(__name__)

MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)


async def process_generation_job(job_id: int):
    """
    Handles the image generation task. This function:
    - Fetches job from DB
    - Mocks a Replicate API call
    - Saves image locally
    - Updates job status
    """
    async with AsyncSessionLocal() as db:
        job: Job = await get_job(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            # --- Mock Replicate call ---
            # Replace this with actual API logic later
            mocked_image_url = "https://placekitten.com/512/512"

            # --- Download image ---
            filename = f"job-{job_id}.png"
            file_path = MEDIA_DIR / filename

            async with httpx.AsyncClient() as client:
                response = await client.get(mocked_image_url)
                response.raise_for_status()

                # Save image
                with open(file_path, "wb") as f:
                    f.write(response.content)

            local_url = f"/media/{filename}"

            # --- Update DB ---
            await update_job_result(db, job, status="completed", result_url=local_url)
            logger.info(f"Job {job_id} completed and saved to {file_path}")

        except Exception as e:
            await update_job_result(db, job, status="failed")
            logger.exception(f"Job {job_id} failed: {str(e)}")
