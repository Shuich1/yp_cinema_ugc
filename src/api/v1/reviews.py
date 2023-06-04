from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas import (
    ReviewResponse,
    ReviewListResponse,
    ReviewCreate,
    ReviewVoteResponse,
    ReviewVoteCreate,
    ReviewVoteUpdate,
)
from common.utils import get_page_params, get_sorting_params
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists
from services.reviews import get_reviews_service, ReviewsService

# ToDo: describe exceptions


router = APIRouter(prefix='/api/v1/reviews', tags=['reviews'])


@router.get('/')
async def get_review_list(
        film_id: UUID | None = Query(default=None),
        user_id: UUID | None = Query(default=None),
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


@router.post('/')
async def create_review(
        schema: ReviewCreate,
        # ToDo: user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewResponse:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    review = await service.create_review(user_id=user_id, **schema.dict())

    return ReviewResponse(review=review)


@router.get('/{review_id}', responses={
    404: {'description': 'Not Found'},
})
async def get_review(
        review_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewResponse:
    try:
        review = await service.get_review(review_id=review_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Нет такой рецензии')

    return ReviewResponse(review=review)


@router.delete('/{review_id}', status_code=HTTPStatus.NO_CONTENT, responses={
    403: {'description': 'Unauthorized'},
    404: {'description': 'Not Found'},
})
async def delete_review(
        review_id: UUID,
        # ToDo: _user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> None:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    # ToDo: может стоит вынести проверку user_id в API?

    try:
        review = await service.get_review(review_id=review_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Нет такой рецензии')

    if review.user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно удалить только свою рецензию')

    await service.delete_review(review_id=review_id)


@router.post('/{review_id}/votes', responses={
    409: {'description': 'Conflict'},
})
async def create_review_vote(
        review_id: UUID,
        schema: ReviewVoteCreate,
        # ToDo: _user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVoteResponse:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        vote = await service.create_review_vote(
            review_id=review_id,
            user_id=_user_id,
            **schema.dict(),
        )
    except ResourceAlreadyExists:
        raise HTTPException(HTTPStatus.CONFLICT, 'Уже голосовал')

    return ReviewVoteResponse(review_vote=vote)


@router.put('/{review_id}/votes/{user_id}', responses={
    403: {'description': 'Unauthorized'},
    404: {'description': 'Not Found'},
})
async def update_review_vote(
        review_id: UUID,
        user_id: UUID,
        schema: ReviewVoteUpdate,
        # ToDo: _user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVoteResponse:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно изменить только свой голос')

    try:
        vote = await service.update_review_vote(review_id=review_id, user_id=user_id, **schema.dict())
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Нет такого голоса')

    return ReviewVoteResponse(review_vote=vote)


@router.get('/{review_id}/votes/{user_id}', responses={
    404: {'description': 'Not Found'},
})
async def get_review_vote(
        review_id: UUID,
        user_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVoteResponse:

    try:
        vote = await service.get_review_vote(review_id=review_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote not found')

    return ReviewVoteResponse(review_vote=vote)


@router.delete('/{review_id}/votes/{user_id}', status_code=HTTPStatus.NO_CONTENT, responses={
    403: {'description': 'Unauthorized'},
    404: {'description': 'Not Found'},
})
async def delete_review_vote(
        review_id: UUID,
        user_id: UUID,
        # ToDo: _user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> None:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно удалить только свой голос')

    try:
        await service.delete_review_vote(review_id=review_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote not found')
