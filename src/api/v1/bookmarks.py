from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import (
    BookmarkResponse,
    BookmarkListResponse,
    BookmarkCreate,
    APIException,
)
from api.utils import get_page_params
from services.bookmarks import get_bookmarks_service, BookmarksService
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists

# ToDo: describe exceptions


router = APIRouter(prefix='/api/v1/bookmarks', tags=['bookmarks'])


@router.get('/')
async def get_bookmark_list(
        user_id: UUID,
        paginate_by: dict = Depends(get_page_params()),
        service: BookmarksService = Depends(get_bookmarks_service),
) -> BookmarkListResponse:

    bookmarks = await service.get_bookmark_list(user_id=user_id, **paginate_by)

    return BookmarkListResponse(bookmarks=bookmarks)


@router.post('/', responses={409: {'description': 'Conflict', 'model': APIException}})
async def create_bookmark(
        schema: BookmarkCreate,
        # ToDo: _user_id from token
        service: BookmarksService = Depends(get_bookmarks_service),
) -> BookmarkResponse:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        bookmark = await service.create_bookmark(user_id=_user_id, **schema.dict())
    except ResourceAlreadyExists:
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
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Bookmark does not exist')

    return BookmarkResponse(bookmark=bookmark)


@router.delete(
    '/{film_id}/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        403: {'description': 'Unauthorized', 'model': APIException},
        404: {'description': 'Not Found', 'model': APIException},
    },
)
async def delete_bookmark(
        film_id: UUID,
        user_id: UUID,
        # ToDo: _user_id from token
        service: BookmarksService = Depends(get_bookmarks_service),
) -> None:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED,
            'Only owners can delete their bookmarks',
        )

    try:
        await service.delete_bookmark(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Bookmark does not exist')
