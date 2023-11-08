from sqladmin import ModelView, BaseView, expose

from app.users.models import Users
from app.rosreestr.query.models import Queries
from app.rosreestr.query.order.models import Orders
from app.fedresurs.models import OrdersFr


class UsersAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.username, Users.role, Users.created_at, Users.activated, Users.queries, Users.queries]
    column_details_exclude_list = [Users.hashed_password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class QueriesAdmin(ModelView, model=Queries):
    column_list = [c.name for c in Queries.__table__.c] + [Queries.orders, Queries.user]
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-book"


class OrdersAdmin(ModelView, model=Orders):
    column_list = [c.name for c in Orders.__table__.c] + [Orders.query]
    name = "Кадастр"
    name_plural = "Кадастры"
    icon = "fa-solid fa-file-lines"


class OrdersFrAdmin(ModelView, model=OrdersFr):
    column_list = [c.name for c in OrdersFr.__table__.c]
    name = "Торги"
    name_plural = "Торги"
    icon = "fa-solid fa-gavel"


class MainAdmin(BaseView):
    name = "Сайт"
    icon = "fa-solid fa-star"

    @expose("/app", methods=["GET"])
    def site_page(self, request):
        return self.templates.TemplateResponse(
            "_redirect_site.html",
            context={"request": request},
        )


class CeleryAdmin(BaseView):
    name = "Celery"
    icon = "fa-solid fa-tasks"

    @expose("/flower", methods=["GET"])
    def flower_page(self, request):
        return self.templates.TemplateResponse(
            "_redirect_flower.html",
            context={"request": request},
        )
