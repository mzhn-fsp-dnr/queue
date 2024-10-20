from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class PreregResponse(BaseModel):
    id: UUID4
    service_id: UUID4
    department_id: UUID4
    code: int
    assigned_to: datetime
    created_at: datetime
    updated_at: Optional[datetime]
