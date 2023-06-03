from abc import ABC, abstractmethod
from uuid import UUID
from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from db import mongo
from models import FilmRating, OverallFilmRating

from services.exceptions import ResourceAlreadyExists, ResourceDoesNotExist


class RatingsService(ABC):
    @abstractmethod
    async def get_rating_list(self, film_id: UUID | None, user_id: UUID | None, offset: int, limit: int) -> list[FilmRating]:
        ...

    @abstractmethod
    async def create_rating(self, film_id: UUID, user_id: UUID, rating: int) -> FilmRating:
        ...

    @abstractmethod
    async def get_rating(self, film_id: UUID, user_id: UUID) -> FilmRating:
        ...

    @abstractmethod
    async def update_rating(self, film_id: UUID, user_id: UUID, rating: int) -> FilmRating:
        ...

    @abstractmethod
    async def delete_rating(self, film_id: UUID, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_overall_rating(self, film_id: UUID) -> OverallFilmRating:
        ...


class MongoDBRatingsService(RatingsService):
    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        self.client = mongo_client

    async def get_rating_list(self, film_id: UUID | None, user_id: UUID | None, offset: int, limit: int) -> list[FilmRating]:
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

        ratings = self.client.films.ratings.aggregate(pipeline)
        return [FilmRating(**rating) async for rating in ratings]

    async def create_rating(self, film_id: UUID, user_id: UUID, rating: int) -> FilmRating:
        rating = FilmRating(film_id=film_id, user_id=user_id, rating=rating)
        result = await self.client.films.ratings.update_one(
            filter=rating.dict(include={'film_id', 'user_id'}),
            update={'$setOnInsert': rating.dict()},
            upsert=True,
        )
        if result.matched_count:
            raise ResourceAlreadyExists(f'Rating for {film_id=}, {user_id=} already exists')
        return rating

    async def get_rating(self, film_id: UUID, user_id: UUID) -> FilmRating:
        rating = await self.client.films.ratings.find_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not rating:
            raise ResourceDoesNotExist(f'Rating for {film_id=}, {user_id=} does not exist')
        return FilmRating(**rating)

    async def update_rating(self, film_id: UUID, user_id: UUID, rating: int) -> FilmRating:
        rating = FilmRating(film_id=film_id, user_id=user_id, rating=rating)
        result = await self.client.films.ratings.find_one_and_update(
            filter=rating.dict(include={'film_id', 'user_id'}),
            update={'$set': rating.dict(exclude={'created'})},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise ResourceDoesNotExist(f'Rating for {film_id=}, {user_id=} does not exist')
        return FilmRating(**result)

    async def delete_rating(self, film_id: UUID, user_id: UUID) -> None:
        result = await self.client.films.ratings.delete_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not result.deleted_count:
            raise ResourceDoesNotExist(f'Rating for {film_id=}, {user_id=} does not exist')

    async def get_overall_rating(self, film_id: UUID) -> OverallFilmRating:
        pipeline = [
            {'$match': {'film_id': film_id}},
            {'$group': {
                '_id': '$film_id',
                'avg_rating': {'$avg': '$rating'},
                'ratings_count': {'$count': {}},
            }},
            {'$limit': 1},
        ]
        result = self.client.films.ratings.aggregate(pipeline)
        try:
            rating_stats = await anext(result)
        except StopAsyncIteration:
            raise ResourceDoesNotExist(f'No ratings for {film_id=}')
        return OverallFilmRating(film_id=film_id, **rating_stats)


async def get_ratings_service() -> RatingsService:
    return MongoDBRatingsService(mongo.client)
