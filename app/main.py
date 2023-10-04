import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pages.router import router as router_pages
from rosreestr.router import router as router_rosreestr
from users.router import router as router_users


app = FastAPI(
    title="Сокол.Капитал"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router_pages)
app.include_router(router_rosreestr)
app.include_router(router_users)


if __name__ == '__main__':
    uvicorn.run("main:app",host='0.0.0.0', port=4557, reload=True)
