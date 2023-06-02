from collections import OrderedDict
from http import HTTPStatus
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException, Query

from models import Review, ReviewVote
from services.reviews import get_reviews_service, ReviewsService, ReviewDoesNotExist, ReviewVoteDoesNotExist, ReviewNotEditable
from common.utils import get_sorting_params

router = APIRouter(prefix='/reviews', tags=['reviews'])

# ToDo: describe exceptions


@router.get('/')
async def get_review_list(
        film_id: UUID,
        offset: int | None = Query(0, ge=0),
        limit: int | None = Query(10, ge=0, le=100),
        sort_by: OrderedDict = Depends(
            get_sorting_params(
                ['created_at', 'rating', 'votes'],
                default='created_at:desc',
            ),
        ),
        service: ReviewsService = Depends(get_reviews_service),
) -> list[Review]:
    return await service.get_review_list(
        film_id=film_id,
        sort_by=sort_by,
        offset=offset,
        limit=limit,
    )


@router.post('/')
async def create_review(
        # ToDo: define schema
        film_id: UUID = Body(embed=True),
        # ToDo: user_id from token
        body: str = Body(embed=True, max_length=2000),
        service: ReviewsService = Depends(get_reviews_service),
) -> Review:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    return await service.create_review(film_id=film_id, user_id=user_id, body=body)


@router.get('/{review_id}')
async def get_review(
        review_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> Review:
    try:
        return await service.get_review(review_id=review_id)
    except ReviewDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Review not found')


@router.delete('/{review_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_review(
        review_id: UUID,
        # ToDo: user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> None:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        return await service.delete_review(review_id=review_id, user_id=user_id)
    except ReviewDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Review not found')
    except ReviewNotEditable:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Can\'t delete review')


@router.post('/{review_id}/vote')
async def rate_review(
        review_id: UUID,
        # ToDo: define schema
        vote: Literal['like', 'dislike'] = Body(embed=True),
        # ToDo: user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVote:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    return await service.rate_review(
        review_id=review_id,
        user_id=user_id,
        vote=vote,
    )


@router.get('/{review_id}/getVote')
async def get_review_vote(
        review_id: UUID,
        # ToDo: user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVote:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        return await service.get_review_vote(review_id=review_id, user_id=user_id)
    except ReviewVoteDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote not found')


@router.delete('/{review_id}/deleteVote', status_code=HTTPStatus.NO_CONTENT)
async def delete_review_vote(
        review_id: UUID,
        # ToDo: user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> None:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    await service.delete_review_vote(review_id=review_id, user_id=user_id)
