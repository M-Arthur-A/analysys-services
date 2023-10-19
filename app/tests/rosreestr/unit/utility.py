import pytest
from app.config import settings

async def test_check_env():
    assert settings.MODE == 'TEST'
