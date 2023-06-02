from abc import ABC, abstractmethod
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from db import mongo
from models import FilmRating, OverallFilmRating


class RatingsServiceException(Exception):
    ...


class RatingDoesNotExist(RatingsServiceException):
    ...


class FilmHasNoRatings(RatingsServiceException):
    ...


class RatingsService(ABC):
    @abstractmethod
    async def set_rating(self, film_id: UUID, user_id: UUID, rating: int) -> FilmRating:
        ...

    @abstractmethod
    async def get_rating(self, film_id: UUID, user_id: UUID) -> FilmRating:
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

    async def set_rating(self, film_id: UUID, user_id: UUID, rating: int) -> FilmRating:
        rating = FilmRating(film_id=film_id, user_id=user_id, rating=rating)
        await self.client.films.ratings.update_one(
            filter=rating.dict(exclude={'rating'}),
            update={'$set': rating.dict()},
            upsert=True,
        )
        return rating

    async def get_rating(self, film_id: UUID, user_id: UUID) -> FilmRating:
        rating = await self.client.films.ratings.find_one({
            'film_id': film_id,
            'user_id': user_id,
        })
        if not rating:
            raise RatingDoesNotExist(f'No ratings for {film_id=}, {user_id=}')
        return FilmRating(**rating)

    async def delete_rating(self, film_id: UUID, user_id: UUID) -> None:
        await self.client.films.ratings.delete_one({
            'film_id': film_id,
            'user_id': user_id,
        })

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
        try:
            rating_stats, *_ = await self.client.films.ratings.aggregate(pipeline).to_list(length=None)
        except ValueError:
            raise FilmHasNoRatings(f'No ratings for {film_id=}')
        return OverallFilmRating(film_id=film_id, **rating_stats)


async def get_ratings_service() -> RatingsService:
    return MongoDBRatingsService(mongo.client)
