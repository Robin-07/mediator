from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mediator.core.database import get_session
from mediator.crud.job import create_job, get_job
from mediator.schemas.job import JobCreate, JobStatusResponse
from mediator.worker import generate_media_task

router = APIRouter()


@router.post("/generate", response_model=JobStatusResponse)
async def generate(job_in: JobCreate, db: AsyncSession = Depends(get_session)):
    job = await create_job(db, job_in)
    generate_media_task.delay(job.id)
    return JobStatusResponse(job_id=job.id, status=job.status)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: int, db: AsyncSession = Depends(get_session)):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.id, status=job.status, result_url=job.result_url
    )
