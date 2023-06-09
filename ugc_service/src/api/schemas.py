from typing import List
from typing_extensions import Literal
from uuid import UUID

from models import Bookmark, OverallRating, Rating, Review, ReviewVote
from models.base import BaseModel
from pydantic import Field


class RatingResponse(BaseModel):
    rating: Rating


class RatingListResponse(BaseModel):
    ratings: List[Rating]


class RatingCreate(BaseModel):
    film_id: UUID
    rating: int = Field(ge=0, le=10)


class RatingUpdate(BaseModel):
    rating: int = Field(ge=0, le=10)


class OverallRatingResponse(BaseModel):
    overall_rating: OverallRating


class ReviewResponse(BaseModel):
    review: Review


class ReviewListResponse(BaseModel):
    reviews: List[Review]


class ReviewCreate(BaseModel):
    film_id: UUID
    body: str = Field(max_length=2000)


class ReviewVoteResponse(BaseModel):
    review_vote: ReviewVote


class ReviewVoteCreate(BaseModel):
    vote: Literal['like', 'dislike']


class ReviewVoteUpdate(ReviewVoteCreate):
    ...


class BookmarkResponse(BaseModel):
    bookmark: Bookmark


class BookmarkListResponse(BaseModel):
    bookmarks: List[Bookmark]


class BookmarkCreate(BaseModel):
    film_id: UUID


class APIException(BaseModel):
    detail: str
