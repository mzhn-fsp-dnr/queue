from typing import List
from fastapi import APIRouter, HTTPException, Path

from api.models.queue_item import QueueItem, StatusEnum, TicketTypeEnum
from api.schemas.office import ServiceSchema
from api.schemas.queue_item import QueueItemCreate, QueueItemUpdate, RequestNewQueueItem

from sqlmodel import Session, select, func, Date, col
from api.database import engine

import datetime

from api.services import office_service

router = APIRouter()


def get_ticket(session: Session, department_id: str, services: List[ServiceSchema]):
    statement = (
        select(QueueItem)
        .where(
            # Из текущего отделения
            QueueItem.department_id == department_id,
            # Сегодня
            func.cast(QueueItem.creation_time, Date) == datetime.date.today(),
            # Со статусом WAITING
            QueueItem.status == StatusEnum.WAITING,
            # У которых нужные услуги
            col(QueueItem.service_id).in_([s.id for s in services]),
            # По записи
            QueueItem.ticket_type == TicketTypeEnum.PRE_REG,
            # Время которых уже наступило
            col(QueueItem.date_pre_reg) <= datetime.datetime.now(),
        )
        .order_by(col(QueueItem.date_pre_reg).asc())
        .limit(1)
    )

    ticket = session.exec(statement).one_or_none()

    if ticket:
        return ticket

    statement = (
        select(QueueItem)
        .where(
            # Из текущего отделения
            QueueItem.department_id == department_id,
            # Сегодня
            func.cast(QueueItem.creation_time, Date) == datetime.date.today(),
            # Со статусом WAITING
            QueueItem.status == StatusEnum.WAITING,
            # У которых нужные услуги
            col(QueueItem.service_id).in_([s.id for s in services]),
            # По очереди
            QueueItem.ticket_type == TicketTypeEnum.IN_PERSON,
        )
        .order_by(col(QueueItem.creation_time).asc())
        .limit(1)
    )

    ticket = session.exec(statement).one_or_none()

    if ticket:
        return ticket

    return None


def get_current(session: Session, department_id: str, window_id: str):
    statement = (
        select(QueueItem)
        .where(
            # Из текущего отделения
            QueueItem.department_id == department_id,
            # Из текущего окна
            QueueItem.window == window_id,
            # Сегодня
            func.cast(QueueItem.creation_time, Date) == datetime.date.today(),
            # Со статусом CALLED
            QueueItem.status == StatusEnum.CALLED,
        )
        .order_by(col(QueueItem.creation_time).asc())
        .limit(1)
    )

    current = session.exec(statement).one_or_none()

    return current


@router.post("/department/{department_id}/windows/{window_id}/request-new")
async def request_new_item(
    department_id: str = Path(..., description="The ID of the department"),
    window_id: str = Path(..., description="The index of the item in the queue"),
):
    print("to find office")
    office = office_service.get(department_id)
    if not office:
        raise HTTPException(status_code=400, detail="Отдел не найден!")

    print("Отдел найден: ", office)

    services = None
    for win in office.windows:
        if win.id == window_id:
            services = win.services

    with Session(engine) as session:
        current = get_current(session, department_id=department_id, window_id=window_id)

        if current:
            raise HTTPException(status_code=400, detail="Окно занято!")

        ticket = get_ticket(session, department_id=department_id, services=services)

        if ticket:
            ticket.status = StatusEnum.CALLED
            ticket.window = window_id
            ticket.start_time = datetime.datetime.now()

            session.add(ticket)
            try:
                session.commit()
                session.refresh(ticket)
            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=400, detail=f"Error request new: {str(e)}"
                )

            return {"ticket": ticket}

        return {"ticket": None}


@router.get("/department/{department_id}/windows/{window_id}/current")
async def get_current_ticket(
    department_id: str,
    window_id: str,
):
    with Session(engine) as session:
        current = get_current(session, department_id=department_id, window_id=window_id)

    return current
