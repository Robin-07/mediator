import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mediator.core.db import get_session
from mediator.crud.job import create_job, get_job
from mediator.schemas.job import JobCreate, JobStatusResponse
from mediator.schemas.replicate import (
    ReplicatePredictionInput,
    ReplicateCallbackPayload,
)
from mediator.worker import (
    process_replicate_job_result_task,
    process_replicate_job_task,
    submit_replicate_job_task,
)
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# --------------------------- Mediator API ---------------------------


@router.post("/generate", response_model=JobStatusResponse)
async def generate(job_in: JobCreate, db: AsyncSession = Depends(get_session)):
    job = await create_job(db, job_in)
    logger.info(f"Created job {job.id} with prompt: '{job.prompt}'")

    submit_replicate_job_task.delay(job.id)
    logger.info(f"Enqueued job {job.id} for background processing")

    return JobStatusResponse(job_id=job.id, status=job.status)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
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


@router.post("/callback")
async def replicate_callback(payload: ReplicateCallbackPayload):
    logger.info(f"Received callback for prediction {payload.id}")

    if payload.status != "completed" or not payload.output:
        raise HTTPException(status_code=400, detail="Invalid callback payload")

    media_url = payload.output[0]

    # Call Celery task to handle upload + DB update
    process_replicate_job_result_task.delay(payload.id, str(media_url))

    return {"detail": "Callback accepted"}


# --------------------------- Mocked Replicate API ---------------------------


@router.post("/predictions")
async def replicate_prediction(payload: ReplicatePredictionInput):
    prediction_id = str(uuid.uuid4())
    logger.info(f"Received mock prediction request. Returning id={prediction_id}")

    payload_json = payload.model_dump(mode="json")
    process_replicate_job_task.delay(prediction_id, payload_json["webhook"])

    return {
        "id": prediction_id,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "version": payload_json["version"],
        "input": payload_json["input"],
    }
