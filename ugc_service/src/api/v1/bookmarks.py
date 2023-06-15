from http import HTTPStatus
from uuid import UUID

from api.auth import JWTBearer
from api.schemas import (APIException, BookmarkCreate, BookmarkListResponse,
                         BookmarkResponse)
from api.utils import get_page_params
from fastapi import APIRouter, Depends, HTTPException
from models import User
from services.bookmarks import get_bookmarks_service, BookmarksService
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists
from logging import getLogger


logger = getLogger(__name__)

router = APIRouter()


@router.get('/')
async def get_bookmark_list(
        user_id: UUID,
        paginate_by: dict = Depends(get_page_params()),
        service: BookmarksService = Depends(get_bookmarks_service),
) -> BookmarkListResponse:

    bookmarks = await service.get_bookmark_list(user_id=user_id, **paginate_by)

    return BookmarkListResponse(bookmarks=bookmarks)


@router.post(
    '/',
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        409: {'description': 'Conflict', 'model': APIException},
    },
)
async def create_bookmark(
        schema: BookmarkCreate,
        user: User = Depends(JWTBearer()),
        service: BookmarksService = Depends(get_bookmarks_service),
) -> BookmarkResponse:
    try:
        bookmark = await service.create_bookmark(
            user_id=user.id,
            **schema.dict(),
        )
    except ResourceAlreadyExists:
        logger.error('Bookmark already exists')
        raise HTTPException(HTTPStatus.CONFLICT, 'Bookmark already exists')

    return BookmarkResponse(bookmark=bookmark)


@router.get(
    '/{film_id}/{user_id}',
    responses={404: {'description': 'Not Found', 'model': APIException}},
)
async def get_bookmark(
        film_id: UUID,
        user_id: UUID,
        service: BookmarksService = Depends(get_bookmarks_service),
) -> BookmarkResponse:
    try:
        bookmark = await service.get_bookmark(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        logger.error('Bookmark does not exist film_id=%s, user_id=%s', film_id, user_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Bookmark does not exist')

    return BookmarkResponse(bookmark=bookmark)


@router.delete(
    '/{film_id}/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        401: {'description': 'Unauthorized', 'model': APIException},
        403: {'description': 'Forbidden', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def delete_bookmark(
        film_id: UUID,
        user_id: UUID,
        user: User = Depends(JWTBearer()),
        service: BookmarksService = Depends(get_bookmarks_service),
) -> None:
    if user_id != user.id:
        logger.error('Only owners can delete their bookmarks user_id=%s, user.id=%s', user_id, user.id)
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            'Only owners can delete their bookmarks',
        )

    try:
        await service.delete_bookmark(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        logger.error('Bookmark does not exist film_id=%s, user_id=%s', film_id, user_id)
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Bookmark does not exist')
