from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="",
                   tags=['Страницы'])

templates = Jinja2Templates(directory="app/templates")


@router.get('/rr')
async def rosreestr_page(request: Request):
    return templates.TemplateResponse('template.html', {"request": request,
                                                        "page": "rr.html",})

