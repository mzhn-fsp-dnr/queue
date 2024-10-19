from fastapi import APIRouter, HTTPException, Path

from api.models.queue_item import QueueItem, StatusEnum, TicketTypeEnum
from api.schemas.queue_item import QueueItemCreate, QueueItemUpdate

from sqlmodel import Session, select, func, Date, col
from api.database import engine

import datetime

router = APIRouter()


@router.post("/department/{department_id}/queue")
async def add_to_queue(department_id: str, item: QueueItemCreate):
    if item.ticket_type == TicketTypeEnum.PRE_REG and item.date_pre_reg is None:
        raise HTTPException(status_code=400, detail="ID для предварительной записи обязателен для типа ПЗ")

    with Session(engine) as session:
        statement = select(QueueItem).where(
            QueueItem.department_id == department_id,
            func.cast(QueueItem.creation_time, Date) == datetime.date.today(),
        ).order_by(col(QueueItem.ticket_code).desc()).limit(1)

        last_item = session.exec(statement).one_or_none()

        if last_item and last_item.ticket_code != "9999":
            new_ticket_code = str(int(last_item.ticket_code) + 1).zfill(4)
        else:
            new_ticket_code = "0001"

        queue_item = QueueItem(
            department_id=department_id,
            ticket_code=new_ticket_code,
            service_id=item.service_id,
            status=StatusEnum.WAITING,  # Status is WAITING by default
            ticket_type=item.ticket_type,
            date_pre_reg=item.date_pre_reg
        )

        session.add(queue_item)
        try:
            session.commit()
            session.refresh(queue_item)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"Error adding to queue: {str(e)}")

    return {"message": "Item added to queue", "item": queue_item}

@router.put("/department/{department_id}/queue/{item_index}")
async def update_queue_item(
    department_id: str = Path(..., description="The ID of the department"),
    item_index: str = Path(..., description="The index of the item in the queue"),
    item: QueueItemUpdate = ...,
):
    with Session(engine) as session:
        statement = select(QueueItem).where(
            QueueItem.department_id == department_id,
            QueueItem.id == item_index,
        )
        queue_item = session.exec(statement).first()

        if not queue_item:
            raise HTTPException(status_code=404, detail="Queue item not found")

        # Update the fields if provided
        update_data = item.dict(exclude_unset=True)

        allowed_updates = [
            "window", 
#            "start_time", 
#            "end_time", 
            "status", 
            "service_id", 
            "employee"
        ]
        for key, value in update_data.items():
            if key in allowed_updates:
                setattr(queue_item, key, value)

                if key == "status" and queue_item.status in [StatusEnum.SERVED, StatusEnum.SKIPPED]:
                    queue_item.end_time = datetime.datetime.now()

        try:
            session.commit()
            session.refresh(queue_item)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating queue item: {str(e)}")

    return {"message": "Queue item updated", "item": queue_item}


@router.get("/department/{department_id}/queue/current")
async def get_current_queue(department_id: str) -> list[QueueItem]:
    with Session(engine) as session:
        statement = select(QueueItem).where(
            QueueItem.department_id == department_id,
            func.cast(QueueItem.creation_time, Date) == datetime.date.today(),
            col(QueueItem.status).in_([StatusEnum.WAITING, StatusEnum.CALLED]),
        )
        results = session.exec(statement).all()

    return results


# ====================================================
