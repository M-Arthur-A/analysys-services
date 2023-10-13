from datetime import date

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi_cache.decorator import cache
from fastapi.responses import FileResponse

from app.users.models import Users
from app.users.dependencies import get_current_user
from app.rosreestr.models import Orders, Queries
from app.rosreestr.schemas import SOrders, SReorder, SDownload

router = APIRouter(prefix="/rr",
                   tags=['Росреестр'])

@router.post('/upload')
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

# @cache(expire=20)
# async def get_orders(current_user: Users = Depends(get_current_user)
@router.get('/queries')
async def get_queries():# -> list[SOrders]:
    temp = [
            {'id': 1,
             'name': 'fierst_try',
             'is_ready': False,
             'orders': [
                {
                    'cadastral': '54:35:061735:130',
                    'cadastral_type': 'simple',
                    'status': 'processing',
                    'created_at': date.today(),
                    'download_link': '/asdasd/as/da/a/sdasdasds'
                },
                {
                    'cadastral': '54:35:061735:131',
                    'cadastral_type': 'simple',
                    'status': 'processed',
                    'created_at': date.today(),
                    'download_link': '/asdasd/as/da/a/sdasdasds'
                },
            ]},
            {'id': 2,
             'name': 'second_try',
             'is_ready': True,
             'orders': [
                {
                    'cadastral': '54:35:061735:130',
                    'cadastral_type': 'history',
                    'status': 'processed',
                    'created_at': date.today(),
                    'download_link': '/asdasd/as/da/a/sdasdasds'
                },
                {
                    'cadastral': '54:35:061735:131',
                    'cadastral_type': 'history',
                    'status': 'processed',
                    'created_at': date.today(),
                    'download_link': '/asdasd/as/da/a/sdasdasds'
                },
            ]},
    ]
    return temp


@router.post('/download')
async def download(d_file: SDownload):
    return FileResponse(path=f'/tmp/rosreestr/{d_file.query_id}',
                        filename=d_file.query_name+'.zip',
                        media_type='application/zip')


@router.post('/reorder')
async def reorder(query: SReorder):
    print(str(query.query_id) + ' reordered')
