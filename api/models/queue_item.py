from pydantic import Field
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import IntEnum
from uuid import UUID, uuid4

class StatusEnum(IntEnum):
    WAITING = 0    # ожидание
    CALLED = 1     # вызван
    SERVED = 2     # обслужен
    SKIPPED = 3    # пропущен

class TicketTypeEnum(IntEnum):
    IN_PERSON = 0 # очно
    PRE_REG   = 1  # предварительная запись

class QueueItem(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    department_id: str = Field(index=True)
    window: Optional[str] = None
    
    ticket_code: str # Уникальный в рамках дня (9999)

    service_id: str

    status: StatusEnum = Field(default=StatusEnum.WAITING)  # Default status is WAITING
    ticket_type: TicketTypeEnum    
    creation_time: datetime = Field(default_factory=datetime.now)

    date_pre_reg: Optional[datetime] = None

    employee: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None