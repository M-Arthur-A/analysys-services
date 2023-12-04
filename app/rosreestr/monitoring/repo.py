from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm import joinedload
from sqlalchemy import Column, DateTime, insert, select, delete
from sqlalchemy.sql import func
from sqlalchemy.orm import lazyload

from app.database import async_session_maker
from app.repository.repo import BaseDAO
from app.rosreestr.query.order.models import Orders
from app.rosreestr.monitoring.models import Monitorings


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
            end_at=datetime.now() + relativedelta(month=monitoring_duration),
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
