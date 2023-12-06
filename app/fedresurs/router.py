import re
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.fedresurs.schemas import SQuery
from app.fedresurs.repo import OrdersFrDAO
from app.tasks.tasks import fr_run


router = APIRouter(prefix="/fr",
                   tags=['Федресурс'])


# @cache(expire=120)
@router.get('/queries')
async def get_queries(current_user: Users = Depends(get_current_user)) -> list[dict]:
    """
    [
        {
            "inn": "123456798",
            "created_at": "1234-12-12",
            "is_ready": False,
        },
        {
            "inn": "987654321",
            "created_at": "1234-12-12",
            "is_ready": True,
        },
    ]

    """
    return await OrdersFrDAO.find_all(user_id=current_user.id)


@router.post('/query')
async def add(queries: SQuery,
              current_user: Users = Depends(get_current_user)):
    uid = str(uuid.uuid1())
    for query in queries.query.split('\n'):
        query = re.sub("[^0-9]", "", query)
        if 10 <= len(query) <= 12:
            await OrdersFrDAO.add(
                query_id=uid,
                inn=query,
                user_id=current_user.id,
                is_ready=False,
                created_at=datetime.now(),
            )
    # send task to celery
    fr_run.delay(uid)

@router.get('/download')
async def download(query_inn: str):
    return FileResponse(
        path=f'{settings.FR_STORAGE}/{query_inn}.xlsx',
        filename=query_inn+'.xlsx',
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
