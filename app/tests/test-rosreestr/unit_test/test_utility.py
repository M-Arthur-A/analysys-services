import pytest
from icecream import ic
import os

from app.config import settings
from app.rosreestr.utility import Utility
from app.rosreestr.schemas import SQuery
from app.rosreestr.monitoring.schemas import SOrderMon
from app.rosreestr.query.order.repo import OrdersDAO
from app.rosreestr.monitoring.repo import MonitoringsDAO


@pytest.mark.parametrize("user_id,prj,q_s,q_h", [
    (
        2,
        "test_prj",
        "77:02:0004001:211",
        "77:02:0004001:210"
    ),
    (
        1,
        None,
        "77:02:0004001:211\n77:02:0004001:210",
        ""
    ),
])
async def test_creating_orders(user_id, prj, q_s, q_h):
    utility = Utility()
    query = SQuery(project=prj,query_s=q_s,query_h=q_h)
    orders_before = len(await OrdersDAO.get_all_by_user(user_id=user_id))
    await utility.create_orders_by_txt(query=query, user_id=user_id)
    orders_after = len(await OrdersDAO.get_all_by_user(user_id=user_id))
    assert (orders_after - orders_before) == 2


async def test_checking_orders():
    utility = Utility()
    await utility.check_orders()
    assert 1 == 1

async def test_dir():
    utility = Utility()
    utility.session._check_dir('testing')
    assert os.path.exists('/tmp/rosreestr/testing')

async def test_monitoring_add_get_delete():
    utility = Utility()
    cadastral="77:02:0004001:210"
    query = SOrderMon(
        project='test_prj',
        monitoring_cadastral=cadastral,
        monitoring_duration=15,
        monitoring_intense=0,
    )
    await utility.add_mon(query, user_id=1)
    # filling monitoringId
    await MonitoringsDAO.update(
        item_id=1,
        monitoringId="externalId",
    )
    mon_id, mon_mon_id = await MonitoringsDAO.get_all_id(cadastral)
    assert mon_id == 1
    assert mon_mon_id == "externalId"
    await MonitoringsDAO.delete(item_id=mon_id)
    assert await MonitoringsDAO.get_all_id(cadastral) == (None, None)
