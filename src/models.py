from datetime import datetime
from uuid import UUID, uuid4
from typing import Literal

from pydantic import BaseModel, Field


class FilmRating(BaseModel):
    film_id: UUID
    user_id: UUID
    rating: int
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)


class OverallFilmRating(BaseModel):
    film_id: UUID
    avg_rating: float
    ratings_count: int


class Review(BaseModel):
    review_id: UUID = Field(default_factory=uuid4)
    film_id: UUID
    user_id: UUID
    body: str
    created: datetime = Field(default_factory=datetime.utcnow)
    likes: int = 0
    dislikes: int = 0


class ReviewVote(BaseModel):
    review_id: UUID
    user_id: UUID
    vote: Literal['like', 'dislike']


class Bookmark(BaseModel):
    film_id: UUID
    user_id: UUID
    created: datetime = Field(default_factory=datetime.utcnow)
