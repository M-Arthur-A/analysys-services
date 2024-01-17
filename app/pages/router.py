from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates

from app.rosreestr.router import get_queries as rr_get_queries
from app.rosreestr.router import get_monitorings as rr_get_monitorings
from app.rosreestr.router import get_balance as rr_get_balance
from app.rosreestr.router import get_balance_mon as rr_get_balance_mon
from app.fedresurs.router import get_queries as fr_get_queries
from app.exceptions import IncorrectTokenFormatException, TokenAbsentException
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
async def rosreestr_page(
        request: Request,
        queries = Depends(rr_get_queries),
        monitorings = Depends(rr_get_monitorings),
        balance = Depends(rr_get_balance),
        balance_mon = Depends(rr_get_balance_mon),
):
    return templates.TemplateResponse('template.html', {
                                            "page": "rr.html",
                                            "SITE_NAME": settings.SITE_NAME,
                                            "TG_BOT": settings.TG_BOT,
                                            "TG_CHANNEL": settings.TG_RR_CHANNEL,
                                            "request": request,
                                            "top_panel": "top_panel.html",
                                            "queries": queries,
                                            "monitorings": monitorings,
                                            "balance": balance,
                                            "balance_mon": balance_mon,
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

async def error_404_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("template.html", {
                                            "page": "error.html",
                                            "SITE_NAME": settings.SITE_NAME,
                                            "top_panel": None,
                                            "request": request,
                                            "error": exc,
                                            }
                                      )

async def error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("template.html", {
                                            "page": "error.html",
                                            "SITE_NAME": settings.SITE_NAME,
                                            "top_panel": None,
                                            "request": request,
                                            "error": exc,
                                            }
                                      )


def include_exception_handler(app):
    app.add_exception_handler(IncorrectTokenFormatException, error_handler)
    app.add_exception_handler(TokenAbsentException, error_handler)
