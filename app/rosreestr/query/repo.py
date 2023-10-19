
from app.repository.repo import BaseDAO
from app.rosreestr.query.models import Queries


class QuariesDAO(BaseDAO):
    model = Queries


    @classmethod
    async def get_one(cls, query_id: int) -> Queries:
        ...

    @classmethod
    async def get_name(cls, query_id: int) -> str:
        ...

    @classmethod
    async def get_all(cls, user_id: int) -> list[Queries]:
        ...

    @classmethod
    async def add(cls, project: str, user_id: int) -> int:
        # returns query_id
        ...

    @classmethod
    async def modify(cls,):
        ...

    @classmethod
    async def delete(cls, query_id: int):
        ...
