import pytest
import asyncio

from fastapi.testclient import TestClient # httpx
from httpx import AsyncClient

from app.main import app as fastapi_app
from app.config import settings
from app.database import async_session_maker



@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"


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
