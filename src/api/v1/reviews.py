from http import HTTPStatus
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException, Query

from common.utils import get_page_params, get_sorting_params
from models import Review, ReviewVote
from services.reviews import get_reviews_service, ReviewsService
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists

router = APIRouter(prefix='/reviews', tags=['reviews'])

# ToDo: describe exceptions


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
) -> list[Review]:
    return await service.get_review_list(
        film_id=film_id,
        user_id=user_id,
        sort_by=sort_by,
        **paginate_by,
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


@router.get('/{review_id}', responses={
    404: {'description': 'Not Found'},
})
async def get_review(
        review_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> Review:
    try:
        return await service.get_review(review_id=review_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Нет такой рецензии')


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
        # ToDo: define schema
        vote: Literal['like', 'dislike'] = Body(embed=True),
        # ToDo: _user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVote:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        return await service.create_review_vote(
            review_id=review_id,
            user_id=_user_id,
            vote=vote,
        )
    except ResourceAlreadyExists:
        raise HTTPException(HTTPStatus.CONFLICT, 'Уже голосовал')


@router.put('/{review_id}/votes/{user_id}', responses={
    403: {'description': 'Unauthorized'},
    404: {'description': 'Not Found'},
})
async def update_review_vote(
        review_id: UUID,
        user_id: UUID,
        # ToDo: define schema
        vote: Literal['like', 'dislike'] = Body(embed=True),
        # ToDo: _user_id from token
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVote:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно изменить только свой голос')

    try:
        return await service.update_review_vote(review_id=review_id, user_id=user_id, vote=vote)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Нет такого голоса')


@router.get('/{review_id}/votes/{user_id}', responses={
    404: {'description': 'Not Found'},
})
async def get_review_vote(
        review_id: UUID,
        user_id: UUID,
        service: ReviewsService = Depends(get_reviews_service),
) -> ReviewVote:

    try:
        return await service.get_review_vote(review_id=review_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Vote not found')


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
