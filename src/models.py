from datetime import datetime
from uuid import UUID, uuid4
from typing import Literal

from pydantic import BaseModel, Field, conset


class FilmRating(BaseModel):
    film_id: UUID
    user_id: UUID
    rating: int


class OverallFilmRating(BaseModel):
    film_id: UUID
    avg_rating: float
    ratings_count: int


class Review(BaseModel):
    review_id: UUID = Field(default_factory=uuid4)
    film_id: UUID
    user_id: UUID
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    likes: int = 0
    dislikes: int = 0


class ReviewVote(BaseModel):
    review_id: UUID
    user_id: UUID
    vote: Literal['like', 'dislike']


class Bookmark(BaseModel):
    film_id: UUID
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
