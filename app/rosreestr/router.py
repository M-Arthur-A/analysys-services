from datetime import date

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.encoders import jsonable_encoder
# from fastapi_cache.decorator import cache
from fastapi.responses import FileResponse

from app.config import settings
from app.users.models import Users
from app.users.dependencies import get_current_user
from app.rosreestr.query.models import Queries
from app.rosreestr.query.repo import BalanceDAO, QueriesDAO
from app.rosreestr.monitoring.repo import MonitoringsDAO
from app.rosreestr.query.order.models import Orders
from app.rosreestr.schemas import SOrders, SQuery, SReorder, SDownload, SSearch
from app.rosreestr.monitoring.schemas import SOrderMon
from app.rosreestr.utility import Utility
from app.tasks.tasks import rr_adding, rr_adding_mon

router = APIRouter(prefix="/rr",
                   tags=['Росреестр'])

@router.post('/upload')
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

# @cache(expire=120)
@router.get('/queries')
async def get_queries(current_user: Users = Depends(get_current_user)) -> dict:
    """
    [
        {
            'id': 1,
            'name': 'first_try',
            'is_ready': False,
            'orders': [
            {
                'cadastral': 'xx:xx:xxxxx:xxxxx',
                'cadastral_type': 'simple',
                'status': 'processing',
                'status_txt': 'в процессе',
                'created_at': 'da.te.2023',
            },
        ]},
    ]
    """
    answer = await QueriesDAO.get_all(user_id=current_user.id)
    answer = jsonable_encoder(answer)
    return answer


@router.post('/query')
async def add(query: SQuery,
              current_user: Users = Depends(get_current_user)):
    query_id = await Utility.create_orders_by_txt(
        query=query,
        user_id=current_user.id
    )
    # send task to celery
    rr_adding.delay(query_id)


@router.get('/download')
async def download(query_id: int, query_name: str):
    await Utility.prepare_for_download(query_id, query_name)
    return FileResponse(path=f'{settings.RR_STORAGE}/{query_name}.zip',
                        filename=query_name+'.zip',
                        media_type='application/zip')


@router.post('/reorder')
async def reorder(query: SReorder):
    await Utility.reorder(query_id=query.query_id)
    # send task to celery
    rr_adding.delay(query.query_id)


@router.post('/refresh')
async def refresh(query: SReorder):
    await Utility.check_orders(query_id=query.query_id)


# @cache(expire=120)
@router.post('/find')
async def find(query: SSearch) -> str:
    return await Utility.find(query=query.query)

@router.delete('/del')
async def delete(query_id: int):
    return await QueriesDAO.delete(query_id=query_id)

@router.get('/create')
async def create_if_not():
    rr_adding.delay()

@router.get('/balance')
async def get_balance():
    return await BalanceDAO.get_actual()

@router.get('/checkbalance')
async def check_balance():
    return await Utility.check_balance()

@router.post('/monitoringquery')
async def add_mon(query: SOrderMon,
                  current_user: Users = Depends(get_current_user)):
    await Utility.add_mon(
        query=query,
        user_id=current_user.id
    )
    # send task to celery
    # rr_adding_mon.delay()

@router.get('/monitors')
async def get_monitorings(current_user: Users = Depends(get_current_user)) -> list[dict]:
    return await MonitoringsDAO.find_all(user_id=current_user.id)
