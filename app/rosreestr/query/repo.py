from datetime import datetime

from sqlalchemy import Column, DateTime, insert, select
from sqlalchemy.sql import func

from app.database import async_session_maker
from app.repository.repo import BaseDAO
from app.rosreestr.query.models import Queries


class QuariesDAO(BaseDAO):
    model = Queries


    @classmethod
    async def get_one(cls, query_id: int) -> dict:
        return await cls.find_by_id(query_id)

    @classmethod
    async def get_name(cls, query_id: int) -> str | None:
        query = select(Queries.name).filter_by(id=query_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_all(cls, user_id: int) -> list[Queries]:
        return await cls.find_all(user_id=user_id)


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


    @classmethod
    async def modify(cls,):
        ...

    @classmethod
    async def delete(cls, query_id: int):
        ...
