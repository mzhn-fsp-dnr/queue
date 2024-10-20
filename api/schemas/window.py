from typing import List
from pydantic import BaseModel

class RequestNewQueueItem(BaseModel):
    department_id: str
    window_id: str
    services: List[str]
