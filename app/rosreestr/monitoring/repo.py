from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple

from sqlalchemy.orm import joinedload
from sqlalchemy import Column, DateTime, insert, select, delete, update
from sqlalchemy.sql import func
from sqlalchemy.orm import lazyload

from app.database import async_session_maker
from app.repository.repo import BaseDAO
from app.rosreestr.query.order.models import Orders
from app.rosreestr.monitoring.models import Monitorings
from app.users.models import Users


class MonitoringsDAO(BaseDAO):
    model = Monitorings

    @classmethod
    async def add(cls,
                  project:             str,
                  cadastral:           str,
                  monitoring_intense:  int,
                  monitoring_duration: int,
                  user_id:             int
    ) -> int:
        query = insert(cls.model).values(
            tag=project,
            cadastral=cadastral,
            start_at=datetime.now(),
            end_at=datetime.now() + relativedelta(months=monitoring_duration),
            modified_at=datetime.now(),
            interval=monitoring_intense,
            status="New",
            status_txt="Заказывается",
            user_id=user_id,
        ). returning(cls.model.id)
        async with async_session_maker() as session:
            new_query_id = await session.execute(query)
            await session.commit()
            return new_query_id.scalar_one()


    @classmethod
    async def get_last_event_id(cls) -> str | None:
        """
        select last_event_id from rr_monitors limit 1;
        """
        query = select(cls.model.last_event_id).limit(1)
        async with async_session_maker() as session:
            last_event_id = await session.execute(query)
            return last_event_id.scalar_one()


    @classmethod
    async def update_last_event_id(cls, last_event_id: str):
        query = update(cls.model)\
            .values(last_event_id=last_event_id)
        async with async_session_maker() as session:
            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_all_id(cls, cadastral: str) -> Tuple[int, str] | Tuple[None, None]:
        query = select(cls.model.id, cls.model.monitoringId)\
            .where(cls.model.cadastral == cadastral)
        async with async_session_maker() as session:
            sql_result = await session.execute(query)
            result = tuple(sql_result.tuples())
            return result[0] if result else (None, None)

    @classmethod
    async def get_count(cls) -> int:
        query = select(func.count(cls.model.monitoringId))\
            .filter(cls.model.monitoringId != None)
        async with async_session_maker() as session:
            sql_result = await session.execute(query)
            result = await session.execute(query)
            return result.scalar_one()

    @classmethod
    async def get_id_from_mon_id(cls, mon_id: str) -> int | None:
        query = select(cls.model.id)\
            .where(cls.model.monitoringId == mon_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one()

    @classmethod
    async def get_username_from_id(cls, item_id: int) -> str | None:
        query = select(Users.username)\
            .select_from(cls.model.id)\
            .join(Users, cls.model.user_id == Users.id, isouter=True)\
            .where(cls.model.id == item_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.scalar_one()
