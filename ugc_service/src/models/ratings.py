from datetime import datetime
from uuid import UUID

from pydantic import Field

from models.base import BaseModel


class Rating(BaseModel):
    film_id: UUID
    user_id: UUID
    rating: int
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)


class OverallRating(BaseModel):
    film_id: UUID
    avg_rating: float
    ratings_count: int
