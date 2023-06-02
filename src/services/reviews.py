from abc import ABC, abstractmethod
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.results import UpdateResult

from db import mongo
from models import Review, ReviewVote
from typing import Literal
from collections import OrderedDict


class ReviewsServiceException(Exception):
    ...


class ReviewDoesNotExist(ReviewsServiceException):
    ...


class ReviewNotEditable(ReviewsServiceException):
    ...


class ReviewVoteDoesNotExist(ReviewsServiceException):
    ...


class ReviewsService(ABC):
    @abstractmethod
    async def get_review_list(self, film_id: UUID, sort_by: OrderedDict[str, str], offset: int, limit: int) -> list[Review]:
        ...

    @abstractmethod
    async def create_review(self, film_id: UUID, user_id: UUID, body: str) -> Review:
        ...

    @abstractmethod
    async def get_review(self, review_id: UUID) -> Review:
        ...

    @abstractmethod
    async def delete_review(self, review_id: UUID, user_id: UUID) -> None:
        ...

    @abstractmethod
    async def rate_review(self, review_id: UUID, user_id: UUID, vote: str) -> ReviewVote:
        ...

    @abstractmethod
    async def get_review_vote(self, review_id: UUID, user_id: UUID) -> ReviewVote:
        ...

    @abstractmethod
    async def delete_review_vote(self, review_id: UUID, user_id: UUID) -> None:
        ...


class MongoDBReviewsService(ReviewsService):
    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        self.client = mongo_client

    async def get_review_list(self, film_id: UUID, sort_by: OrderedDict[str, str], offset: int, limit: int) -> list[Review]:
        add_fields, sort = self._get_sorting_params(sort_by)
        pipeline = [
            {'$match': {'film_id': film_id}},
            {'$addFields': add_fields},
            {'$sort': sort or {'_id': 1}},
            {'$skip': offset},
            {'$limit': limit},
        ]
        reviews = self.client.films.reviews.aggregate(pipeline)
        return [Review(**review) async for review in reviews]

    async def create_review(self, film_id: UUID, user_id: UUID, body: str) -> Review:
        review = Review(film_id=film_id, user_id=user_id, body=body)
        await self.client.films.reviews.insert_one(review.dict())
        return review

    async def get_review(self, review_id: UUID) -> Review:
        review = await self.client.films.reviews.find_one({'review_id': review_id})
        if not review:
            raise ReviewDoesNotExist(f'No reviews with {review_id=}')
        return Review(**review)

    async def delete_review(self, review_id: UUID, user_id: UUID) -> None:
        review = await self.client.films.reviews.find_one({'review_id': review_id})
        if not review:
            raise ReviewDoesNotExist(f'No reviews with {review_id=}')
        elif not review.get('user_id') == user_id:
            raise ReviewNotEditable(f'Author {review_id=} does not match {user_id=}')
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                await self.client.films.reviews.delete_one({'review_id': review_id})
                await self.client.films.review_votes.delete_many({'review_id': review_id})

    async def rate_review(self, review_id: UUID, user_id: UUID, vote: str) -> ReviewVote:
        review_vote = ReviewVote(review_id=review_id, user_id=user_id, vote=vote)
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                result = await self.client.films.review_votes.update_one(
                    filter=review_vote.dict(exclude={'vote'}),
                    update={'$set': review_vote.dict()},
                    upsert=True,
                )
                votes_update = self._get_votes_update(result, vote)
                if votes_update:
                    await self.client.films.reviews.update_one(
                        filter={'review_id': review_id},
                        update={'$inc': votes_update},
                    )
        return review_vote

    async def get_review_vote(self, review_id: UUID, user_id: UUID) -> ReviewVote:
        review_vote = await self.client.films.review_votes.find_one({
            'review_id': review_id,
            'user_id': user_id,
        })
        if not review_vote:
            raise ReviewVoteDoesNotExist(f'No votes for {review_id=}, {user_id=}')
        return ReviewVote(**review_vote)

    async def delete_review_vote(self, review_id: UUID, user_id: UUID) -> None:
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                result = await self.client.films.review_votes.find_one_and_delete({
                    'review_id': review_id,
                    'user_id': user_id,
                })
                if result:
                    vote = result.get('vote')
                    votes_update = {'likes' if vote == 'like' else 'dislikes': -1}
                    await self.client.films.reviews.update_one(
                        filter={'review_id': review_id},
                        update={'$inc': votes_update},
                    )

    @staticmethod
    def _get_sorting_params(sort_by: OrderedDict[str, str]) -> tuple[dict, dict]:
        add_fields = {}
        sort = {}
        for field, order in sort_by.items():
            if field == 'created_at':
                sort['created_at'] = 1 if order == 'asc' else -1
            elif field == 'rating':
                add_fields['rating'] = {'$subtract': ['$likes', '$dislikes']}
                sort['rating'] = 1 if order == 'asc' else -1
            elif field == 'votes':
                add_fields['votes'] = {'$sum': ['$likes', '$dislikes']}
                sort['votes'] = 1 if order == 'asc' else -1
        return add_fields, sort

    @staticmethod
    def _get_votes_update(result: UpdateResult, vote: str) -> dict | None:
        if result.matched_count and not result.modified_count:
            return None
        elif not result.matched_count and not result.modified_count:
            return {'likes' if vote == 'like' else 'dislikes': 1}
        elif vote == 'like':
            return {'likes': 1, 'dislikes': -1}
        else:
            return {'likes': -1, 'dislikes': 1}


async def get_reviews_service() -> ReviewsService:
    return MongoDBReviewsService(mongo.client)
