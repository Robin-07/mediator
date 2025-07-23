from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from mediator.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    result_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
