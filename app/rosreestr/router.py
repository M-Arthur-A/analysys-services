from fastapi import APIRouter, Request, UploadFile


router = APIRouter(prefix="/rr",
                   tags=['Росреестр'])

@router.post('/upload')
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

@router.post('/answer')
async def rosreestr_answer(request: Request):
    return 'done'
