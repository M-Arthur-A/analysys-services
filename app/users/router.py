from fastapi import APIRouter, Request


router = APIRouter(prefix="/users",
                   tags=['Подьзователи'])


@router.post('/register')
async def regiser(request: Request):
    return 'done'

@router.post('/login')
async def login(request: Request):
    return 'done'
