from abc import ABC, abstractmethod
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from db import mongo
from models import Bookmark


class BookmarksService(ABC):
    @abstractmethod
    async def get_bookmark_list(self, user_id: UUID, offset: int, limit: int) -> list[Bookmark]:
        ...

    @abstractmethod
    async def set_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
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
            {'$sort': {'created_at': -1}},
            {'$skip': offset},
            {'$limit': limit},
        ]
        bookmarks = self.client.films.bookmarks.aggregate(pipeline)
        return [Bookmark(**bookmark) async for bookmark in bookmarks]

    async def set_bookmark(self, film_id: UUID, user_id: UUID) -> Bookmark:
        bookmark = Bookmark(film_id=film_id, user_id=user_id)
        await self.client.films.bookmarks.update_one(
            filter=bookmark.dict(exclude={'created_at'}),
            update={'$set': bookmark.dict()},
            upsert=True,
        )
        return bookmark

    async def delete_bookmark(self, film_id: UUID, user_id: UUID) -> None:
        await self.client.films.bookmarks.delete_one({
            'film_id': film_id,
            'user_id': user_id,
        })


async def get_bookmarks_service() -> BookmarksService:
    return MongoDBBookmarksService(mongo.client)
