import pytest
import asyncio
import json

from fastapi.testclient import TestClient # httpx
from httpx import AsyncClient
from sqlalchemy import insert

from app.main import app as fastapi_app
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.users.models import Users



@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f'app/tests/mock_{model}.json', encoding='utf8') as file:
            return json.load(file)

    users = open_mock_json("users")

    async with async_session_maker() as session:
        for Model, values in [
                                (Users, users),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)

        await session.commit()

@pytest.fixture(scope="session")
def event_loop():
    """
    Взято из документации к pytest-asyncio
    Create an instance of the default event loop for each test case.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function')
async def ac():
    """
    async-client
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope='session')
async def authenticated_ac():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        await ac.post('/auth/login', json={
            'email': 'test@test.com',
            'password': 'test',
        })
        assert ac.cookies['booking_access_token']
        yield ac


@pytest.fixture(scope='function')
async def session():
    async with async_session_maker() as session:
        yield session
