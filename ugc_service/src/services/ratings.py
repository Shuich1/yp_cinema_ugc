from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from db import mongo
from models import OverallRating, Rating
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from services.exceptions import ResourceAlreadyExists, ResourceDoesNotExist


class RatingsService(ABC):
    @abstractmethod
    async def get_rating_list(self,
                              film_id: Optional[UUID],
                              user_id: Optional[UUID],
                              offset: int,
                              limit: int,
                              ) -> List[Rating]:
        ...

    @abstractmethod
    async def create_rating(self,
                            film_id: UUID,
                            user_id: UUID,
                            rating: int,
                            ) -> Rating:
        ...

    @abstractmethod
    async def get_rating(self, film_id: UUID, user_id: UUID) -> Rating:
        ...

    @abstractmethod
    async def update_rating(self,
                            film_id: UUID,
                            user_id: UUID,
                            rating: int,
                            ) -> Rating:
        ...

    @abstractmethod
    async def delete_rating(self, film_id: UUID, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_overall_rating(self, film_id: UUID) -> OverallRating:
        ...


class MongoDBRatingsService(RatingsService):
    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        self._ratings = mongo_client.films.ratings

    async def get_rating_list(self,
                              film_id: Optional[UUID],
                              user_id: Optional[UUID],
                              offset: int,
                              limit: int,
                              ) -> List[Rating]:
        pipeline = [
            {'$sort': {'updated': -1}},
            {'$skip': offset},
            {'$limit': limit},
        ]
        match = {}
        if film_id:
            match['film_id'] = film_id
        if user_id:
            match['user_id'] = user_id
        if match:
            pipeline.insert(0, {'$match': match})

        ratings = self._ratings.aggregate(pipeline)
        return [Rating(**rating) async for rating in ratings]

    async def create_rating(self,
                            film_id: UUID,
                            user_id: UUID,
                            rating: int,
                            ) -> Rating:
        res_rating = Rating(film_id=film_id, user_id=user_id, rating=rating)
        result = await self._ratings.update_one(
            filter=res_rating.dict(include={'film_id', 'user_id'}),
            update={'$setOnInsert': res_rating.dict()},
            upsert=True,
        )
        if result.matched_count:
            raise ResourceAlreadyExists()
        return res_rating

    async def get_rating(self, film_id: UUID, user_id: UUID) -> Rating:
        rating = await self._ratings.find_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not rating:
            raise ResourceDoesNotExist()
        return Rating(**rating)

    async def update_rating(self,
                            film_id: UUID,
                            user_id: UUID,
                            rating: int,
                            ) -> Rating:
        res_rating = Rating(film_id=film_id, user_id=user_id, rating=rating)
        result = await self._ratings.find_one_and_update(
            filter=res_rating.dict(include={'film_id', 'user_id'}),
            update={'$set': res_rating.dict(exclude={'created'})},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise ResourceDoesNotExist()
        return Rating(**result)

    async def delete_rating(self, film_id: UUID, user_id: UUID) -> None:
        result = await self._ratings.delete_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not result.deleted_count:
            raise ResourceDoesNotExist()

    async def get_overall_rating(self, film_id: UUID) -> OverallRating:
        pipeline = [
            {'$match': {'film_id': film_id}},
            {'$group': {
                '_id': '$film_id',
                'avg_rating': {'$avg': '$rating'},
                'ratings_count': {'$count': {}},
            }},
            {'$limit': 1},
        ]
        result = self._ratings.aggregate(pipeline)
        try:
            rating_stats = await anext(result)
        except StopAsyncIteration:
            raise ResourceDoesNotExist()
        return OverallRating(film_id=film_id, **rating_stats)


async def get_ratings_service() -> RatingsService:
    return MongoDBRatingsService(mongo.client)
