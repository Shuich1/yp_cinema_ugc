from abc import ABC, abstractmethod
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from db import mongo
from models import Bookmark

from services.exceptions import ResourceAlreadyExists, ResourceDoesNotExist


class BookmarksService(ABC):
    @abstractmethod
    async def get_bookmark_list(self, user_id: UUID, offset: int, limit: int) -> list[Bookmark]:
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
        self.client = mongo_client

    async def get_bookmark_list(self, user_id: UUID, offset: int, limit: int) -> list[Bookmark]:
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$sort': {'created': -1}},
            {'$skip': offset},
            {'$limit': limit},
        ]
        bookmarks = self.client.films.bookmarks.aggregate(pipeline)
        return [Bookmark(**bookmark) async for bookmark in bookmarks]

    async def create_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        bookmark = Bookmark(film_id=film_id, user_id=user_id)
        result = await self.client.films.bookmarks.update_one(
            filter=bookmark.dict(exclude={'created'}),
            update={'$setOnInsert': bookmark.dict()},
            upsert=True,
        )
        if result.matched_count:
            raise ResourceAlreadyExists(f'Bookmark for {film_id=}, {user_id=} already exists')
        return bookmark

    async def get_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        result = await self.client.films.bookmarks.find_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not result:
            raise ResourceDoesNotExist(f'Bookmark for {film_id=}, {user_id=} does not exist')
        return Bookmark(**result)

    async def delete_bookmark(self, film_id: UUID, user_id: UUID) -> None:
        result = await self.client.films.bookmarks.delete_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not result.deleted_count:
            raise ResourceDoesNotExist(f'Bookmark for {film_id=}, {user_id=} does not exist')


async def get_bookmarks_service() -> BookmarksService:
    return MongoDBBookmarksService(mongo.client)
