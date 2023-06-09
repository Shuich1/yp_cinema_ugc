from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from db import mongo
from models import Bookmark
from motor.motor_asyncio import AsyncIOMotorClient
from services.exceptions import ResourceAlreadyExists, ResourceDoesNotExist


class BookmarksService(ABC):
    @abstractmethod
    async def get_bookmark_list(self,
                                user_id: UUID,
                                offset: int,
                                limit: int,
                                ) -> List[Bookmark]:
        ...

    @abstractmethod
    async def create_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        ...

    @abstractmethod
    async def get_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        ...

    @abstractmethod
    async def delete_bookmark(self, film_id: UUID, user_id: UUID) -> None:
        ...


class MongoDBBookmarksService(BookmarksService):
    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        self._bookmarks = mongo_client.films.bookmarks

    async def get_bookmark_list(self,
                                user_id: UUID,
                                offset: int,
                                limit: int,
                                ) -> List[Bookmark]:
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$sort': {'created': -1}},
            {'$skip': offset},
            {'$limit': limit},
        ]
        bookmarks = self._bookmarks.aggregate(pipeline)
        return [Bookmark(**bookmark) async for bookmark in bookmarks]

    async def create_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        bookmark = Bookmark(film_id=film_id, user_id=user_id)
        result = await self._bookmarks.update_one(
            filter=bookmark.dict(exclude={'created'}),
            update={'$setOnInsert': bookmark.dict()},
            upsert=True,
        )
        if result.matched_count:
            raise ResourceAlreadyExists()
        return bookmark

    async def get_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        result = await self._bookmarks.find_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not result:
            raise ResourceDoesNotExist()
        return Bookmark(**result)

    async def delete_bookmark(self, film_id: UUID, user_id: UUID) -> None:
        result = await self._bookmarks.delete_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not result.deleted_count:
            raise ResourceDoesNotExist()


async def get_bookmarks_service() -> BookmarksService:
    return MongoDBBookmarksService(mongo.client)
