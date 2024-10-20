from typing import Optional, List
from api.models.queue_item import TicketTypeEnum, StatusEnum
from pydantic import BaseModel, Field
from datetime import datetime

from pydantic import BaseModel


class QueueItemCreate(BaseModel):
    service_id: str
    ticket_type: TicketTypeEnum
    date_pre_reg: Optional[datetime] = Field(
        None, description="Обязателен для предварительной записи"
    )


class QueueItemUpdate(BaseModel):
    service_id: Optional[str] = None
    status: Optional[StatusEnum] = None
    window: Optional[str] = None
    employee: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class RequestNewQueueItem(BaseModel):
    services: List[str]
