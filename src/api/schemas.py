from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from models import Rating, OverallRating, Review, ReviewVote, Bookmark


class RatingResponse(BaseModel):
    rating: Rating


class RatingListResponse(BaseModel):
    ratings: list[Rating]


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
    reviews: list[Review]


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
    bookmarks: list[Bookmark]


class BookmarkCreate(BaseModel):
    film_id: UUID
