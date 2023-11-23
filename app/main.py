import uvicorn
from sqladmin import Admin
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.pages.router import router as router_pages, include_exception_handler, error_404_handler
from app.users.router import router as router_users
from app.rosreestr.router import router as router_rosreestr
from app.fedresurs.router import router as router_fedresurs
from app.database import engine
from app.admin.views import UsersAdmin, QueriesAdmin, OrdersAdmin, MainAdmin, CeleryAdmin, OrdersFrAdmin
from app.admin.auth import authentication_backend



app = FastAPI(
    title="Сокол.Капитал"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router_fedresurs)
app.include_router(router_rosreestr)
app.include_router(router_users)
app.include_router(router_pages)

include_exception_handler(app)

@app.exception_handler(404)
async def error_404(request: Request, exc: HTTPException):
    return await error_404_handler(request, exc)

@app.exception_handler(500)
async def error_500(request: Request, exc: HTTPException):
    return await error_404_handler(request, exc)

admin = Admin(app, engine,
              authentication_backend=authentication_backend,
              templates_dir="app/templates"
             )
admin.add_view(MainAdmin)
admin.add_view(CeleryAdmin)
admin.add_view(UsersAdmin)
admin.add_view(QueriesAdmin)
admin.add_view(OrdersAdmin)
admin.add_view(OrdersFrAdmin)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)
