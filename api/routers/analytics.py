from fastapi import APIRouter
from api.models.queue_item import QueueItem, TicketTypeEnum
from sqlmodel import Session, case, select, func, literal, union_all, cast, Float, text, extract, Interval
from api.database import engine

import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/department/{department_id}/days")
def analytics_department_days(department_id: str):
    """
        Получение кол-ва посетителей по дням недели
    """
    with Session(engine) as session:
        # Создаем CTE для дней недели (0-6)
        days_of_week = union_all(
            select(literal(0).label('day_of_week')),
            select(literal(1).label('day_of_week')),
            select(literal(2).label('day_of_week')),
            select(literal(3).label('day_of_week')),
            select(literal(4).label('day_of_week')),
            select(literal(5).label('day_of_week')),
            select(literal(6).label('day_of_week'))
        ).cte('days_of_week')
        statement = (
            select(
                days_of_week.c.day_of_week,  # День недели из CTE
                func.coalesce(func.count(QueueItem.id), 0).label('visit_count')  # Количество посещений или 0
            )
            .join(QueueItem, func.extract('dow', QueueItem.creation_time) == days_of_week.c.day_of_week, isouter=True)
            .where(QueueItem.department_id == department_id)
            .group_by(days_of_week.c.day_of_week)
            .order_by(days_of_week.c.day_of_week)
        )
        res = session.exec(statement).all()
        
        return [{"day": col[0], "visit_count": col[1]} for col in res]
    
@router.get("/department/{department_id}/services")
def analytics_department_services(department_id: str):
    """
        Получение распределения клиентов по разным типам услуг
    """
    with Session(engine) as session:
        # Сначала считаем общее количество записей (всех клиентов)
        total_clients = session.exec(
            select(func.count(QueueItem.id)).where(QueueItem.department_id == department_id)
            ).first()
        # Запрос для подсчета количества клиентов по типам услуг и вычисления процента
        statement = (
            select(
                QueueItem.service_id,  # Тип услуги (service_id)
                (cast(func.count(QueueItem.id), Float) / total_clients * 100).label('percentage')  # Процентное распределение
            )
            .where(QueueItem.department_id == department_id)
            .group_by(QueueItem.service_id)
            .order_by(text('percentage DESC'))
        )

        # Выполнение запроса
        res = session.exec(statement).all()
        return [{"service_id": col[0], "percent": round(col[1],2) } for col in res]


@router.get("/department/{department_id}/awg_wait_time")
def analytics_department_awg_wait_time(department_id: str):
    """
        Получение среднего времени ожидания по часам (8:00 - 19:00)
    """
    with Session(engine) as session:
    # Запрос для вычисления среднего времени ожидания по часам (8:00 - 19:00)
        statement = (
            select(
                extract('hour', QueueItem.creation_time).label('hour'),  # Извлекаем час из времени создания
                func.avg(
                    cast(QueueItem.start_time - QueueItem.creation_time, Interval)
                ).label('avg_wait_time')  # Вычисляем среднее время ожидания (разница между start_time и creation_time)
            )
            .where(
                QueueItem.department_id == department_id,
                extract('hour', QueueItem.creation_time).between(8, 19)  # Учитываем только время с 8:00 до 19:00
            )
            .group_by('hour')  # Группировка по часам
            .order_by('hour')  # Сортировка по часам
        )

        # Выполнение запроса
        res = session.exec(statement).all() 
        print("--------------------------------res-----------------------------")
        print(res)
        print("--------------------------------res-----------------------------")
        return [{"hour": col[0], "avg_wait_time": str(col[1]) } for col in res]
        
@router.get("/department/{department_id}/total")
def analytics_department_all_time(department_id: str):
    # Текущая дата
    today = datetime.datetime.now()
    # Дата 30 дней назад
    thirty_days_ago = today - datetime.timedelta(days=30)

    with Session(engine) as session:
        
    # Запрос для получения статистики
        query = (
        select(
            func.date(QueueItem.creation_time).label("visit_date"),
            func.count(QueueItem.id).label("total_visits"),
            func.sum(
                case(
                    (QueueItem.ticket_type == TicketTypeEnum.PRE_REG, 1),
                    else_=0
                )
            ).label("pre_reg_visits"),
            func.sum(
                case(
                    (QueueItem.ticket_type == TicketTypeEnum.IN_PERSON, 1),
                    else_=0
                )
            ).label("in_person_visits"),
        )
        .where(QueueItem.creation_time >= thirty_days_ago, QueueItem.creation_time <= today, QueueItem.department_id== department_id)
        .group_by(func.date(QueueItem.creation_time))
        .order_by(func.date(QueueItem.creation_time))
    )
    
    results = session.exec(query).all()
    print(results)
    # Преобразование результатов в читаемый формат
    stats = [
        {
            "date": result.visit_date,
            "total_visits": result.total_visits,
            "pre_reg_visits": result.pre_reg_visits,
            "in_person_visits": result.in_person_visits,
        }
        for result in results
    ]
    
    return stats