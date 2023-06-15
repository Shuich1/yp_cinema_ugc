from http import HTTPStatus
from typing import Optional
from uuid import UUID

from api.auth import JWTBearer
from api.schemas import (APIException, ReviewCreate, ReviewListResponse,
                         ReviewResponse, ReviewVoteCreate, ReviewVoteResponse,
                         ReviewVoteUpdate)
from api.utils import get_page_params, get_sorting_params
from fastapi import APIRouter, Depends, HTTPException, Query
from models import User
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists
from services.reviews import get_reviews_service, ReviewsService
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter()


@router.get('/')
async def get_review_list(
        film_id: Optional[UUID] = Query(default=None),
        user_id: Optional[UUID] = Query(default=None),
        paginate_by: dict = Depends(get_page_params()),
        sort_by: dict = Depends(
            get_sorting_params(
                ['created', 'rating', 'votes'],
                default='created:desc',
            ),
        ),
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewListResponse:
    reviews = await service.get_review_list(
        film_id=film_id,
        user_id=user_id,
        sort_by=sort_by,
        **paginate_by,
    )

    return ReviewListResponse(reviews=reviews)


@router.post(
    '/',
    responses={401: {'description': 'Unauthorized', 'model': APIException}},
)
async def create_review(
        schema: ReviewCreate,
        user: User = Depends(JWTBearer()),
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewResponse:

    review = await service.create_review(user_id=user.id, **schema.dict())

    return ReviewResponse(review=review)


@router.get(
    '/{review_id}',
    responses={404: {'description': 'Not Found', 'model': APIException}},
)
async def get_review(
        review_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewResponse:
    try:
        review = await service.get_review(review_id=review_id)
    except ResourceDoesNotExist:
        logger.error('Review not found review_id=%s', review_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Review not found')

    return ReviewResponse(review=review)


@router.delete(
    '/{review_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        403: {'description': 'Forbidden', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def delete_review(
        review_id: UUID,
        user: User = Depends(JWTBearer()),
        service: ReviewsService = Depends(get_reviews_service),
) -> None:
    try:
        review = await service.get_review(review_id=review_id)
    except ResourceDoesNotExist:
        logger.error('Review not found review_id=%s', review_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Review not found')

    if review.user_id != user.id:
        logger.error('Only owners can delete their reviews: review.user_id=%s, user.id=%s', review.user_id, user.id)
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            'Only owners can delete their reviews',
        )

    await service.delete_review(review_id=review_id)


@router.post(
    '/{review_id}/votes',
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        409: {'description': 'Conflict', 'model': APIException},
    },
)
async def create_review_vote(
        review_id: UUID,
        schema: ReviewVoteCreate,
        user: User = Depends(JWTBearer()),
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVoteResponse:
    try:
        vote = await service.create_review_vote(
            review_id=review_id,
            user_id=user.id,
            **schema.dict(),
        )
    except ResourceAlreadyExists:
        logger.error('Vote already exists. review_id=%s, user_id=%s', review_id, user.id)
        raise HTTPException(HTTPStatus.CONFLICT, 'Vote already exists')

    return ReviewVoteResponse(review_vote=vote)


@router.put(
    '/{review_id}/votes/{user_id}',
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        403: {'description': 'Forbidden', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def update_review_vote(
        review_id: UUID,
        user_id: UUID,
        schema: ReviewVoteUpdate,
        user: User = Depends(JWTBearer()),
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVoteResponse:
    if user_id != user.id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            'Only owners can update their votes',
        )

    try:
        vote = await service.update_review_vote(
            review_id=review_id,
            user_id=user_id,
            **schema.dict(),
        )
    except ResourceDoesNotExist:
        logger.error('Vote does not exist. review_id=%s, user_id=%s', review_id, user.id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote does not exist')

    return ReviewVoteResponse(review_vote=vote)


@router.get(
    '/{review_id}/votes/{user_id}',
    responses={404: {'description': 'Not Found', 'model': APIException}},
)
async def get_review_vote(
        review_id: UUID,
        user_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVoteResponse:

    try:
        vote = await service.get_review_vote(
            review_id=review_id,
            user_id=user_id,
        )
    except ResourceDoesNotExist:
        logger.error('Vote not found. review_id=%s, user_id=%s', review_id, user_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote not found')

    return ReviewVoteResponse(review_vote=vote)


@router.delete(
    '/{review_id}/votes/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        403: {'description': 'Forbidden', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def delete_review_vote(
        review_id: UUID,
        user_id: UUID,
        user: User = Depends(JWTBearer()),
        service: ReviewsService = Depends(get_reviews_service),
) -> None:
    if user_id != user.id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            'Only owners can delete their votes',
        )

    try:
        await service.delete_review_vote(review_id=review_id, user_id=user_id)
    except ResourceDoesNotExist:
        logger.error('Vote not found. review_id=%s, user_id=%s', review_id, user_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote not found')
