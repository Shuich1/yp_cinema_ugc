from http import HTTPStatus
from typing import Optional
from uuid import UUID

from api.auth import JWTBearer
from api.schemas import (APIException, OverallRatingResponse, RatingCreate,
                         RatingListResponse, RatingResponse, RatingUpdate)
from api.utils import get_page_params
from fastapi import APIRouter, Depends, HTTPException, Query
from models import User
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists
from services.ratings import get_ratings_service, RatingsService
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter()


@router.get('/')
async def get_rating_list(
        film_id: Optional[UUID] = Query(default=None),
        user_id: Optional[UUID] = Query(default=None),
        paginate_by: dict = Depends(get_page_params()),
        service: RatingsService = Depends(get_ratings_service),
) -> RatingListResponse:
    ratings = await service.get_rating_list(
        film_id=film_id,
        user_id=user_id,
        **paginate_by,
    )

    return RatingListResponse(ratings=ratings)


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        409: {'description': 'Conflict', 'model': APIException},
    },
)
async def create_rating(
        schema: RatingCreate,
        user: User = Depends(JWTBearer()),
        service: RatingsService = Depends(get_ratings_service),
) -> RatingResponse:
    try:
        rating = await service.create_rating(user_id=user.id, **schema.dict())
    except ResourceAlreadyExists:
        logger.error('Rating already exists user.id=%s', user.id)
        raise HTTPException(HTTPStatus.CONFLICT, 'Rating already exists')

    return RatingResponse(rating=rating)


@router.get(
    '/{film_id}/{user_id}',
    responses={404: {'description': 'Not Found', 'model': APIException}},
)
async def get_rating(
        film_id: UUID,
        user_id: UUID,
        service: RatingsService = Depends(get_ratings_service),
) -> RatingResponse:
    try:
        rating = await service.get_rating(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        logger.error('Rating does not exist user_id=%s, film_id=%s', user_id, film_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Rating does not exist')

    return RatingResponse(rating=rating)


@router.put(
    '/{film_id}/{user_id}',
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        403: {'description': 'Forbidden', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def update_rating(
        film_id: UUID,
        user_id: UUID,
        schema: RatingUpdate,
        user: User = Depends(JWTBearer()),
        service: RatingsService = Depends(get_ratings_service),
) -> RatingResponse:
    if user_id != user.id:
        logger.error('Only owners can update their ratings user_id=%s, user.id=%s', user_id, user.id)
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            'Only owners can update their ratings',
        )

    try:
        rating = await service.update_rating(
            film_id=film_id,
            user_id=user_id,
            **schema.dict(),
        )
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Rating does not exist')

    return RatingResponse(rating=rating)


@router.delete(
    '/{film_id}/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        403: {'description': 'Forbidden', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def delete_rating(
        film_id: UUID,
        user_id: UUID,
        user: User = Depends(JWTBearer()),
        service: RatingsService = Depends(get_ratings_service),
) -> None:
    if user_id != user.id:
        logger.error('Only owners can delete their ratings user_id=%s, user.id=%s', user_id, user.id)
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            'Only owners can delete their ratings',
        )

    try:
        await service.delete_rating(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Rating does not exist')


@router.get(
    '/getOverallRating',
    responses={404: {'description': 'Not Found', 'model': APIException}},
)
async def get_overall_rating(
        film_id: UUID,
        service: RatingsService = Depends(get_ratings_service),
) -> OverallRatingResponse:
    try:
        rating = await service.get_overall_rating(film_id=film_id)
    except ResourceDoesNotExist:
        logger.error('No ratings yet film_id=%s', film_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'No ratings yet')

    return OverallRatingResponse(overall_rating=rating)
