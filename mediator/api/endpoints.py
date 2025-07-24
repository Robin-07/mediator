import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mediator.core.database import get_session
from mediator.crud.job import create_job, get_job
from mediator.schemas.job import JobCreate, JobStatusResponse
from mediator.schemas.replicate_mock import ReplicateInput
from mediator.services.job_handler import replicate_prediction_complete
from mediator.worker import generate_media_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("v1/generate", response_model=JobStatusResponse)
async def generate(job_in: JobCreate, db: AsyncSession = Depends(get_session)):
    job = await create_job(db, job_in)
    logger.info(f"Created job {job.id} with prompt: '{job.prompt}'")

    generate_media_task.delay(job.id)
    logger.info(f"Enqueued job {job.id} for background processing")

    return JobStatusResponse(job_id=job.id, status=job.status)


@router.get("v1/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: int, db: AsyncSession = Depends(get_session)):
    job = await get_job(db, job_id)
    if not job:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")

    logger.debug(f"Fetched status for job {job.id}: {job.status}")
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        result_url=job.media_url,
    )


@app.post("/v1/predictions")
async def replicate_prediction(
    payload: ReplicateInput, background_tasks: BackgroundTasks
):
    prediction_id = str(uuid.uuid4())
    logger.info(f"Received mock prediction request. Returning id={prediction_id}")

    # Schedule background task to hit webhook
    background_tasks.add_task(
        replicate_prediction_complete, prediction_id, payload.webhook
    )

    return {
        "id": prediction_id,
        "status": "processing",
        "created_at": "2025-07-23T12:00:00Z",
        "version": payload.version,
        "input": payload.input,
    }
