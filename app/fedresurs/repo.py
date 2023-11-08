
from app.repository.repo import BaseDAO
from app.fedresurs.models import OrdersFr


class OrdersFrDAO(BaseDAO):
    model = OrdersFr
