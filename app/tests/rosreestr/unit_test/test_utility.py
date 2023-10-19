import pytest

from app.config import settings
from app.rosreestr.utility import Utility
from app.rosreestr.schemas import SQuery


@pytest.mark.parametrize("user_id,query", [
    (
        1,
        SQuery(
            project=None,
            query_s=r"77:02:0004001:211\r\n77:02:0004001:210",
            query_h=r"77:02:0004001:211\r\n77:02:0004001:210"
        )
    ),
    (
        1,
        SQuery(
            project=None,
            query_s=r"77:02:0004001:211\r\n77:02:0004001:210",
            query_h=r""
        )
    ),
])
async def test_creating_orders(user_id, query):
    utility = Utility()
    await utility.create_orders_by_txt(user_id=user_id, query=query)
