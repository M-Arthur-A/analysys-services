from datetime import date

from app.repository.repo import BaseDAO
from app.rosreestr.query.order.models import Orders


class OrdersDAO(BaseDAO):
    model = Orders


    @classmethod
    async def get_one(cls, query_id: int, order_id: int) -> Orders:
        ...

    @classmethod
    async def get_all(cls, query_id: int, *filters) -> list[Orders]:
        ...

    @classmethod
    async def add(cls,
                  query_id:       int,
                  order_id:       str,
                  session_id:     str,
                  cadastral:      str,
                  cadastral_type: str,
                  status:         str,
                  status_txt:     str,
                  created_at:     date,
                  ):
        ...

    @classmethod
    async def modify(cls,
                     order_id:       str,
                     new_status:     str,
                     new_status_txt: str,
                     modified_at:    date,
                     ):
        ...

    @classmethod
    async def delete(cls, query_id: int):
        ...
