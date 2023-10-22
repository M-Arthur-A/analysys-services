import pytest

from app.config import settings
from app.rosreestr.utility import Utility
from app.rosreestr.schemas import SQuery
from app.rosreestr.query.order.repo import OrdersDAO


@pytest.mark.parametrize("user_id,prj,q_s,q_h", [
    (
        2,
        "test_prj",
        r"77:02:0004001:211",
        r"77:02:0004001:210"
    ),
    (
        1,
        None,
        r"77:02:0004001:211\r\n77:02:0004001:210",
        r""
    ),
])
async def test_creating_orders(user_id, prj, q_s, q_h):
    utility = Utility()
    query = SQuery(project=prj,query_s=q_s,query_h=q_h)
    orders_before = len(await OrdersDAO.get_all_by_user(user_id=user_id))
    await utility.create_orders_by_txt(query=query, user_id=user_id)
    orders_after = len(await OrdersDAO.get_all_by_user(user_id=user_id))
    assert (orders_after - orders_before) == 2
