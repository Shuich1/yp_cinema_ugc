from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.users_films import UserFilmService, get_userfilm_service


class BaseResponse(BaseModel):
    detail: str


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }


class UserFilmTimestampSchema(BaseModel):
    user_id: UUID
    film_id: UUID
    start_time: int
    end_time: int
    timestamp: datetime


router = APIRouter()


@router.post('/',
             summary='Создание временной метки о просмотренной пользователем части кинопроизведения',
             description='Создание временной метки о просмотренной пользователем части кинопроизведения',
             responses={
                HTTPStatus.OK: {'model': BaseResponse, 'description': 'Результат операции'},
                HTTPStatus.BAD_REQUEST: {'model': HTTPError}
             })
async def create_user_film_timestamp(
        user_film_data: UserFilmTimestampSchema,
        ugc_service: UserFilmService = Depends(get_userfilm_service),
):
    try:
        await ugc_service.create_user_film_timestamp(user_film_data)
    except BaseException as exception:
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=exception.__str__())

    return BaseResponse(detail='ok')
