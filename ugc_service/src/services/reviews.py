from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from db import mongo
from models import Review, ReviewVote
from motor.motor_asyncio import AsyncIOMotorClient
from services.exceptions import ResourceAlreadyExists, ResourceDoesNotExist


class ReviewsService(ABC):
    @abstractmethod
    async def get_review_list(self,
                              film_id: Optional[UUID],
                              user_id: Optional[UUID],
                              sort_by: dict,
                              offset: int,
                              limit: int,
                              ) -> List[Review]:
        ...

    @abstractmethod
    async def create_review(self,
                            film_id: UUID,
                            user_id: UUID,
                            body: str,
                            ) -> Review:
        ...

    @abstractmethod
    async def get_review(self, review_id: UUID) -> Review:
        ...

    @abstractmethod
    async def delete_review(self, review_id: UUID) -> None:
        ...

    @abstractmethod
    async def create_review_vote(self,
                                 review_id: UUID,
                                 user_id: UUID,
                                 vote: str,
                                 ) -> ReviewVote:
        ...

    @abstractmethod
    async def get_review_vote(self,
                              review_id: UUID,
                              user_id: UUID,
                              ) -> ReviewVote:
        ...

    @abstractmethod
    async def update_review_vote(self,
                                 review_id: UUID,
                                 user_id: UUID,
                                 vote: str,
                                 ) -> ReviewVote:
        ...

    @abstractmethod
    async def delete_review_vote(self, review_id: UUID, user_id: UUID) -> None:
        ...


class MongoDBReviewsService(ReviewsService):
    def __init__(self, mongo_client: AsyncIOMotorClient) -> None:
        self._client = mongo_client
        self._reviews = mongo_client.films.reviews
        self._review_votes = mongo_client.films.review_votes

    async def get_review_list(self,
                              film_id: Optional[UUID],
                              user_id: Optional[UUID],
                              sort_by: dict,
                              offset: int,
                              limit: int,
                              ) -> List[Review]:
        add_fields, sort = self._get_sorting_params(sort_by)
        pipeline = [
            {'$addFields': add_fields},
            {'$sort': sort or {'_id': 1}},
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

        reviews = self._reviews.aggregate(pipeline)
        return [Review(**review) async for review in reviews]

    @staticmethod
    def _get_sorting_params(sort_by: dict) -> Tuple[dict, dict]:
        add_fields = {}
        sort = {}
        for field, order in sort_by.items():
            if field == 'created':
                sort['created'] = 1 if order == 'asc' else -1
            elif field == 'rating':
                add_fields['rating'] = {'$subtract': ['$likes', '$dislikes']}
                sort['rating'] = 1 if order == 'asc' else -1
            elif field == 'votes':
                add_fields['votes'] = {'$sum': ['$likes', '$dislikes']}
                sort['votes'] = 1 if order == 'asc' else -1
        return add_fields, sort

    async def create_review(self,
                            film_id: UUID,
                            user_id: UUID,
                            body: str,
                            ) -> Review:
        review = Review(film_id=film_id, user_id=user_id, body=body)
        await self._reviews.insert_one(review.dict())
        return review

    async def get_review(self, review_id: UUID) -> Review:
        review = await self._reviews.find_one({
            'review_id': review_id,
        })
        if not review:
            raise ResourceDoesNotExist()
        return Review(**review)

    async def delete_review(self, review_id: UUID) -> None:
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                await self._reviews.delete_one({'review_id': review_id})
                await self._review_votes.delete_many({'review_id': review_id})

    async def create_review_vote(self,
                                 review_id: UUID,
                                 user_id: UUID,
                                 vote: str,
                                 ) -> ReviewVote:
        review_vote = ReviewVote(
            review_id=review_id,
            user_id=user_id,
            vote=vote,
        )
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                result = await self._review_votes.update_one(
                    filter=review_vote.dict(exclude={'vote'}),
                    update={'$setOnInsert': review_vote.dict()},
                    upsert=True,
                )
                if result.matched_count:
                    raise ResourceAlreadyExists()

                await self._reviews.update_one(
                    filter={'review_id': review_id},
                    update={'$inc': {
                        'likes' if vote == 'like' else 'dislikes': 1,
                    }},
                )
                return review_vote

    async def get_review_vote(self,
                              review_id: UUID,
                              user_id: UUID,
                              ) -> ReviewVote:
        review_vote = await self._review_votes.find_one({
            'review_id': review_id,
            'user_id': user_id,
        })
        if not review_vote:
            raise ResourceDoesNotExist()
        return ReviewVote(**review_vote)

    async def update_review_vote(self,
                                 review_id: UUID,
                                 user_id: UUID,
                                 vote: str,
                                 ) -> ReviewVote:
        review_vote = ReviewVote(
            review_id=review_id,
            user_id=user_id,
            vote=vote,
        )
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                result = await self._review_votes.update_one(
                    filter=review_vote.dict(exclude={'vote'}),
                    update={'$set': review_vote.dict()},
                )

                if not result.matched_count:
                    raise ResourceDoesNotExist()

                if result.modified_count:
                    await self._reviews.update_one(
                        filter={'review_id': review_id},
                        update={'$inc': {
                            'likes' if vote == 'like' else 'dislikes': 1,
                            'dislikes' if vote == 'like' else 'likes': -1,
                        }},
                    )

                return review_vote

    async def delete_review_vote(self, review_id: UUID, user_id: UUID) -> None:
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                result = await self._review_votes.find_one_and_delete({
                    'review_id': review_id,
                    'user_id': user_id,
                })

                if not result:
                    raise ResourceDoesNotExist()

                vote = result.get('vote')
                await self._reviews.update_one(
                    filter={'review_id': review_id},
                    update={'$inc': {
                        'likes' if vote == 'like' else 'dislikes': -1,
                    }},
                )


async def get_reviews_service() -> ReviewsService:
    return MongoDBReviewsService(mongo.client)
