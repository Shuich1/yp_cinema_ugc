from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException

from models import FilmRating, OverallFilmRating
from services.ratings import get_ratings_service, RatingsService, RatingDoesNotExist, FilmHasNoRatings

router = APIRouter(prefix='/ratings', tags=['ratings'])

# ToDo: describe exceptions


@router.post('/{film_id}', description='Rate the film')
async def set_rating(
        film_id: UUID,
        # ToDo: define schema
        rating: int = Body(embed=True, ge=0, le=10),
        # ToDo: user_id from token
        service: RatingsService = Depends(get_ratings_service),
) -> FilmRating:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    return await service.set_rating(
        user_id=user_id,
        film_id=film_id,
        rating=rating,
    )


@router.get(
    '/{film_id}',
    description='Get current user\'s rating for the film',
)
async def get_rating(
        film_id: UUID,
        # ToDo: user_id from token
        service: RatingsService = Depends(get_ratings_service),
) -> FilmRating:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        return await service.get_rating(film_id=film_id, user_id=user_id)
    except RatingDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Rating not found')


@router.delete(
    '/{film_id}',
    description='If exists, delete current user\'s rating for the film',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_rating(
        film_id: UUID,
        # ToDo: user_id from token
        service: RatingsService = Depends(get_ratings_service),
) -> None:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    await service.delete_rating(film_id=film_id, user_id=user_id)


@router.get(
    '/{film_id}/getOverallRating',
    description='Calculate overall rating for the film',
)
async def get_overall_rating(
        film_id: UUID,
        service: RatingsService = Depends(get_ratings_service),
) -> OverallFilmRating:
    try:
        return await service.get_overall_rating(film_id=film_id)
    except FilmHasNoRatings:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Film not rated yet')
