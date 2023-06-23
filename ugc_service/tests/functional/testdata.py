from datetime import datetime
from random import randint, choice
from typing import Literal
from uuid import UUID, uuid4

from faker import Faker
from pydantic import BaseModel, Field

fake = Faker()


class Bookmark(BaseModel):
    film_id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.utcnow)

    @property
    def id(self) -> tuple[str, str]:
        return str(self.film_id), str(self.user_id)


class Rating(BaseModel):
    film_id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(default_factory=uuid4)
    rating: int = Field(default_factory=lambda: randint(0, 10))
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

    @property
    def id(self) -> tuple[str, str]:
        return str(self.film_id), str(self.user_id)


class Review(BaseModel):
    review_id: UUID = Field(default_factory=uuid4)
    film_id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(default_factory=uuid4)
    body: str = Field(default_factory=fake.text)
    created: datetime = Field(default_factory=fake.date_time_this_year)
    likes: int = 0
    dislikes: int = 0


class ReviewVote(BaseModel):
    review_id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(default_factory=uuid4)
    vote: str = Field(default_factory=lambda: choice(('like', 'dislike')))

    @property
    def id(self) -> tuple[str, str]:
        return str(self.review_id), str(self.user_id)
