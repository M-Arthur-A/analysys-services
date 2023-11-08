from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.rosreestr.router import get_queries as rr_get_queries
from app.fedresurs.router import get_queries as fr_get_queries
from app.config import settings


router = APIRouter(prefix="",
                   tags=['Страницы'])

templates = Jinja2Templates(directory="app/templates")


@router.get('/')
async def login_page(request: Request):
    return templates.TemplateResponse('template.html', {"request": request,
                                                        "top_panel": None,
                                                        "page": "log-reg.html",
                                                        "modal": "modal_reg.html",
                                                        })

@router.get('/rr')
async def rosreestr_page(request: Request, queries = Depends(rr_get_queries)):
    return templates.TemplateResponse('template.html', {
                                            "page": "rr.html",
                                            "SITE_NAME": settings.SITE_NAME,
                                            "TG_BOT": settings.TG_BOT,
                                            "TG_CHANNEL": settings.TG_RR_CHANNEL,
                                            "request": request,
                                            "top_panel": "top_panel.html",
                                            "queries": queries,
                                            }
                                      )

@router.get('/fr')
async def fedresurs_page(request: Request, queries = Depends(fr_get_queries)):
    return templates.TemplateResponse('template.html', {
                                            "page": "fr.html",
                                            "SITE_NAME": settings.SITE_NAME,
                                            "TG_BOT": settings.TG_BOT,
                                            "TG_CHANNEL": settings.TG_RR_CHANNEL,
                                            "request": request,
                                            "top_panel": "top_panel.html",
                                            "orders": queries,
                                            }
                                      )
