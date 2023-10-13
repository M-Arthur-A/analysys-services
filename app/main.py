import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.pages.router import router as router_pages
from app.rosreestr.router import router as router_rosreestr
from app.users.router import router as router_users


app = FastAPI(
    title="Сокол.Капитал"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router_pages)
app.include_router(router_rosreestr)
app.include_router(router_users)


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
