from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from models import Bookmark
from services.bookmarks import get_bookmarks_service, BookmarksService
from uuid import UUID
from common.utils import get_page_params

# ToDo: describe exceptions

router = APIRouter(prefix='/bookmarks', tags=['bookmarks'])


@router.get('/')
async def get_bookmark_list(
        # ToDo: user_id from token
        paginate_by: dict = Depends(get_page_params()),
        service: BookmarksService = Depends(get_bookmarks_service),
) -> list[Bookmark]:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    return await service.get_bookmark_list(user_id=user_id, **paginate_by)


@router.post('/{film_id}')
async def set_bookmark(
        film_id: UUID,
        # ToDo: user_id from token
        service: BookmarksService = Depends(get_bookmarks_service),
) -> Bookmark:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    return await service.set_bookmark(film_id=film_id, user_id=user_id)


@router.delete('/{film_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_bookmark(
        film_id: UUID,
        # ToDo: user_id from token
        service: BookmarksService = Depends(get_bookmarks_service),
) -> None:
    # ToDo: user_id from token
    user_id = UUID('ad5953d0-0af7-44bc-8963-6f606f59747d')

    await service.delete_bookmark(film_id=film_id, user_id=user_id)
