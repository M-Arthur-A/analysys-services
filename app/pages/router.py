from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.rosreestr.router import get_queries
from app.config import settings


router = APIRouter(prefix="",
                   tags=['Страницы'])

templates = Jinja2Templates(directory="app/templates")


@router.get('/')
async def login_page(request: Request):
    return templates.TemplateResponse('template.html', {"request": request,
                                                        "top_panel": None,
                                                        "page": "login.html",
                                                        })
@router.get('/rr')
async def rosreestr_page(request: Request, queries = Depends(get_queries)):
    return templates.TemplateResponse('template.html', {
                                            "SITE_NAME": settings.SITE_NAME,
                                            "TG_BOT": settings.TG_BOT,
                                            "TG_CHANNEL": settings.TG_CHANNEL,
                                            "request": request,
                                            "top_panel": "top_panel.html",
                                            "page": "rr.html",
                                            "queries": queries,
                                                        })
