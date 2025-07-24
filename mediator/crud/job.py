from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from mediator.models.job import Job
from mediator.schemas.job import JobCreate


async def create_job(db: AsyncSession, job_in: JobCreate) -> Job:
    new_job = Job(prompt=job_in.prompt, parameters=job_in.parameters)
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    return new_job


async def get_job(db: AsyncSession, job_id: int) -> Job:
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalars().first()


async def get_job_by_prediction_id(db: AsyncSession, prediction_id: str) -> Job | None:
    result = await db.execute(select(Job).where(Job.prediction_id == prediction_id))
    return result.scalar_one_or_none()


async def update_job_result(
    db: AsyncSession,
    job: Job,
    status: str,
    prediction_id: str = None,
    media_url: str = None,
):
    job.status = status
    if prediction_id:
        job.prediction_id = prediction_id
    if media_url:
        job.result_url = media_url
    await db.commit()
    await db.refresh(job)
