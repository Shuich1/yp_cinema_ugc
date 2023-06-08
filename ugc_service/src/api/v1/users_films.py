from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from models.users_films import UserFilmTimestamp
from pydantic import BaseModel
from services.users_films import UserFilmService, get_userfilm_service
from async_fastapi_jwt_auth import AuthJWT

from logging import getLogger
logger = getLogger(__name__)


class BaseResponse(BaseModel):
    detail: str


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }


router = APIRouter()


@router.post('/',
             summary='Создание временной метки о просмотренной пользователем части кинопроизведения',
             description='Создание временной метки о просмотренной пользователем части кинопроизведения',
             responses={
                HTTPStatus.OK: {'model': BaseResponse, 'description': 'Результат операции'},
                HTTPStatus.BAD_REQUEST: {'model': HTTPError},
                HTTPStatus.FORBIDDEN: {'model': HTTPError}
             })
async def create_user_film_timestamp(
        user_film_data: UserFilmTimestamp,
        ugc_service: UserFilmService = Depends(get_userfilm_service),
        Authorize: AuthJWT = Depends()
):
    await Authorize.jwt_required()
    current_user = await Authorize.get_jwt_subject()
    if current_user != str(user_film_data.user_id):
        logger.error('user_id в токене не соответсвует user_id в timestamp')
        return HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="user_id в токене не соответсвует user_id в timestamp"
        )
    try:
        await ugc_service.create_user_film_timestamp(user_film_data)
    except BaseException as exception:
        logger.error(exception.__str__())
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=exception.__str__())

    return BaseResponse(detail='ok')


@router.get('/{user_id}/{film_id}/last_timestamp',
            summary='Получить последнюю временную метку просмотренной пользователем части кинопроизведения',
            description='Получить последнюю временную метку просмотренной пользователем части кинопроизведения',
            responses={
                HTTPStatus.OK: {'model': UserFilmTimestamp, 'description': 'Временная метка'},
                HTTPStatus.NO_CONTENT: {'description': "Item not found"},
                HTTPStatus.BAD_REQUEST: {'model': HTTPError},
                HTTPStatus.FORBIDDEN: {'model': HTTPError}
            })
async def get_last_user_film_timestamp(
        user_id: UUID, film_id: UUID,
        ugc_service: UserFilmService = Depends(get_userfilm_service),
        Authorize: AuthJWT = Depends()
):
    await Authorize.jwt_required()
    current_user = await Authorize.get_jwt_subject()
    raw_jwt = await Authorize.get_raw_jwt()
    user_roles = raw_jwt['roles']
    if current_user != str(user_id) and 'admin' not in user_roles:
        logger.error("Попытка получить timestump не принадлежащие пользователю")
        return HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Попытка получить timestump не принадлежащие пользователю"
        )
    try:
        timestamp = await ugc_service.get_last_timestamp(user_id, film_id)
    except BaseException as exception:
        logger.error(exception.__str__())
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=exception.__str__())
    if not timestamp:
        return
    return timestamp
