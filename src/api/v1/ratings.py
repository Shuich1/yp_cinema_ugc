from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException, Query

from models import FilmRating, OverallFilmRating
from services.ratings import get_ratings_service, RatingsService
from common.utils import get_page_params, get_sorting_params

from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists

router = APIRouter(prefix='/ratings', tags=['ratings'])


@router.get('/')
async def get_rating_list(
        film_id: UUID | None = Query(default=None),
        user_id: UUID | None = Query(default=None),
        paginate_by: dict = Depends(get_page_params()),
        service: RatingsService = Depends(get_ratings_service),
) -> list[FilmRating]:
    return await service.get_rating_list(film_id=film_id, user_id=user_id, **paginate_by)


@router.post('/', responses={
    409: {'description': 'Conflict'},
})
async def create_rating(
        # ToDo: define schema
        film_id: UUID = Body(embed=True),
        rating: int = Body(embed=True, ge=0, le=10),
        # ToDo: _user_id from token
        service: RatingsService = Depends(get_ratings_service),
) -> FilmRating:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        return await service.create_rating(film_id=film_id, user_id=_user_id, rating=rating)
    except ResourceAlreadyExists:
        raise HTTPException(HTTPStatus.CONFLICT, 'Оценка уже стоит')


@router.get('/{film_id}/{user_id}', responses={
    404: {'description': 'Not Found'},
})
async def get_rating(
        film_id: UUID,
        user_id: UUID,
        service: RatingsService = Depends(get_ratings_service),
) -> FilmRating:
    try:
        return await service.get_rating(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Такой оценки нет!!')


@router.put('/{film_id}/{user_id}', responses={
    404: {'description': 'Not Found'},
    403: {'description': 'Unauthorized'},
})
async def update_rating(
        film_id: UUID,
        user_id: UUID,
        # ToDo: define schema
        rating: int = Body(embed=True, ge=0, le=10),
        # ToDo: _user_id from token
        service: RatingsService = Depends(get_ratings_service),
) -> FilmRating:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно изменять только свои оценки')
    try:
        return await service.update_rating(film_id=film_id, user_id=user_id, rating=rating)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Такой оценки нет!!')


@router.delete(
    '/{film_id}/{user_id}',
    description='If exists, delete current user\'s rating for the film',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        404: {'description': 'Not Found'},
        403: {'description': 'Unauthorized'},
    },
)
async def delete_rating(
        film_id: UUID,
        user_id: UUID,
        # ToDo: _user_id from token
        service: RatingsService = Depends(get_ratings_service),
) -> None:
    # ToDo: user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно [удалять] только свои оценки')
    try:
        await service.delete_rating(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Такой оценки нет ))')


@router.get(
    '/getOverallRating',
    description='Calculate overall rating for the film',
)
async def get_overall_rating(
        film_id: UUID,
        service: RatingsService = Depends(get_ratings_service),
) -> OverallFilmRating:
    try:
        return await service.get_overall_rating(film_id=film_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Нет оценок')
