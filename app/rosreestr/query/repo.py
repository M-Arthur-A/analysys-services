from datetime import datetime

from sqlalchemy.orm import joinedload
from app.rosreestr.query.order.models import Orders

from sqlalchemy import Column, DateTime, insert, select
from sqlalchemy.sql import func
from sqlalchemy.orm import lazyload

from app.database import async_session_maker
from app.repository.repo import BaseDAO
from app.rosreestr.query.models import Queries


class QueriesDAO(BaseDAO):
    model = Queries


    @classmethod
    async def get_name(cls, query_id: int) -> str | None:
        query = select(Queries.name).filter_by(id=query_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @classmethod
    async def get_all(cls, user_id: int) -> dict:
        """
        select * from rr_queries q
        left join rr_orders o
        on q.id = o.query_id
        where q.user_id = 3;
        """
        query = select(Queries)\
            .where(Queries.user_id == user_id)\
            .order_by(Queries.id.desc())\
            .options(joinedload(Queries.orders)) # one-to-many
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.unique().scalars().all()


    @classmethod
    async def add(cls, project: str, user_id: int) -> int: # returns query_id
        query = insert(cls.model).values(
            name=project,
            user_id=user_id,
            created_at=datetime.now(),
            modified_at=datetime.now()
        ). returning(cls.model.id)
        async with async_session_maker() as session:
            new_query_id = await session.execute(query)
            await session.commit()
            return new_query_id.scalar_one()
