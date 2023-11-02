from datetime import date

from sqlalchemy import join, select

from app.database import async_session_maker
from app.repository.repo import BaseDAO
from app.rosreestr.query.order.models import Orders
from app.rosreestr.schemas import SOrderFull
from app.rosreestr.query.models import Queries


class OrdersDAO(BaseDAO):
    model = Orders


    @classmethod
    async def get_all_by_user(cls, user_id: int, *filters) -> list[SOrderFull]:
        """
        select * from rr_queries q
        left join rr_orders r on r.query_id = q.id
        where q.user_id = 1;
        """
        query = select(Orders)\
            .select_from(Queries)\
            .join(Orders, Queries.id == Orders.query_id, isouter=True)\
            .where(Queries.user_id == user_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def get_all_unready(cls) -> list[Orders]:
        """
        select * from rr_orders o
            where
                  (o.is_ready is NULL) and
                  (o.status != 'Error');
        """
        query = select(Orders)\
            .where(
                (Orders.is_ready == None) & \
                (Orders.status != 'Error') & \
                (Orders.status != 'New') & \
                (Orders.status != None)
            )
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.scalars().all()
