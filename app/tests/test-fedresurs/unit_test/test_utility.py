import uuid
from datetime import datetime
import pytest
from icecream import ic

from app.config import settings
from app.fedresurs.utility import Utility
from app.fedresurs.repo import OrdersFrDAO


async def test_checking_orders():
    uid = str(uuid.uuid1())
    await OrdersFrDAO.add(
        query_id=uid,
        inn='1234567890',
        user_id=1,
        is_ready=False,
        created_at=datetime.now(),
    )
    utility = Utility()
    await utility.scrap(uid)
