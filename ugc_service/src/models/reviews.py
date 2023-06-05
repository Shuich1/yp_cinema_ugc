from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import Field

from models.base import BaseModel


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
