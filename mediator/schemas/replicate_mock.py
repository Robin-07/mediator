from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class ReplicateInput(BaseModel):
    version: str
    input: Dict[str, str]
    webhook: HttpUrl
    webhook_events_filter: Optional[List[str]] = None
