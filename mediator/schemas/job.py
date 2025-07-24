from typing import Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    prompt: str
    parameters: Optional[dict] = Field(default_factory=dict)


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    result_url: Optional[str] = None
