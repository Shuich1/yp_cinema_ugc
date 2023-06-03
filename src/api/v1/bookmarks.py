from fastapi import APIRouter, Depends, HTTPException, Body
from http import HTTPStatus
from models import Bookmark
from services.bookmarks import get_bookmarks_service, BookmarksService
from services.exceptions import ResourceDoesNotExist, ResourceAlreadyExists
from uuid import UUID
from common.utils import get_page_params

# ToDo: describe exceptions

router = APIRouter(prefix='/bookmarks', tags=['bookmarks'])


@router.get('/')
async def get_bookmark_list(
        user_id: UUID,
        paginate_by: dict = Depends(get_page_params()),
        service: BookmarksService = Depends(get_bookmarks_service),
) -> list[Bookmark]:

    return await service.get_bookmark_list(user_id=user_id, **paginate_by)


@router.post('/', responses={
    409: {'description': 'Conflict'},
})
async def create_bookmark(
        # ToDo: define schema
        film_id: UUID = Body(embed=True),
        # ToDo: _user_id from token
        service: BookmarksService = Depends(get_bookmarks_service),
) -> Bookmark:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    try:
        return await service.create_bookmark(film_id=film_id, user_id=_user_id)
    except ResourceAlreadyExists:
        raise HTTPException(HTTPStatus.CONFLICT, 'Закладка уже есть такая')


@router.get('/{film_id}/{user_id}', responses={
    404: {'description': 'Not Found'},
})
async def get_bookmark(
        film_id: UUID,
        user_id: UUID,
        service: BookmarksService = Depends(get_bookmarks_service),
) -> Bookmark:
    try:
        return await service.get_bookmark(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Такой закладки нету пока')


@router.delete('/{film_id}/{user_id}', status_code=HTTPStatus.NO_CONTENT, responses={
    403: {'description': 'Unauthorized'},
    404: {'description': 'Not Found'},
})
async def delete_bookmark(
        film_id: UUID,
        user_id: UUID,
        # ToDo: _user_id from token
        service: BookmarksService = Depends(get_bookmarks_service),
) -> None:
    # ToDo: _user_id from token
    _user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    if user_id != _user_id:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'Можно удалять только свои закладки')
    try:
        await service.delete_bookmark(film_id=film_id, user_id=user_id)
    except ResourceDoesNotExist:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'Такой закладки нету')
