from fastapi import APIRouter
from http import HTTPStatus

router = APIRouter(tags=['common'])


@router.get('/ping', status_code=HTTPStatus.NO_CONTENT, summary='Service status')
async def ping():
    pass
