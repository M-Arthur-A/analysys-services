import sys
from loguru import logger

from app.fedresurs.repo import OrdersFrDAO
from app.config import settings
sys.path.append(settings.FR_LIB_PATH)
from runner import run


class Utility:

    @classmethod
    async def scrap(cls, uid):
        orders = await OrdersFrDAO.find_all(query_id=uid)
        for order in orders:
            run([order.inn], settings.FR_STORAGE)
            await OrdersFrDAO.update(order.id, is_ready=True)
            logger.info(f"fr.utility::торги по {order.inn} сохранены")
