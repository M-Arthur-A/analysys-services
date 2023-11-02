import uvicorn
from sqladmin import Admin
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.pages.router import router as router_pages
from app.rosreestr.router import router as router_rosreestr
from app.users.router import router as router_users
from app.database import engine
from app.admin.views import UsersAdmin, QueriesAdmin, OrdersAdmin, MainAdmin, CeleryAdmin
from app.admin.auth import authentication_backend



app = FastAPI(
    title="Сокол.Капитал"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router_pages)
app.include_router(router_rosreestr)
app.include_router(router_users)

admin = Admin(app, engine,
              authentication_backend=authentication_backend,
              templates_dir="app/templates"
             )
admin.add_view(MainAdmin)
admin.add_view(CeleryAdmin)
admin.add_view(UsersAdmin)
admin.add_view(QueriesAdmin)
admin.add_view(OrdersAdmin)

origins = [
    "http://localhost:3000", # 3000 - порт, на котором работает фронтенд на React.js
    "http://0.0.0.0:8000/",
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)
