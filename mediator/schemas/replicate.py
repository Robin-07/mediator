from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class ReplicatePredictionInput(BaseModel):
    version: str
    input: Dict[str, str]
    webhook: HttpUrl
    webhook_events_filter: Optional[List[str]] = None


class ReplicateCallbackPayload(BaseModel):
    id: str
    status: str
    output: list[HttpUrl]
