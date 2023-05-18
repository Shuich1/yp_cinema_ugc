from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class User(BaseModel):
    id: UUID


class MovieTimecode(BaseModel):
    movie_id: UUID
    timecode: int


class MovieTimecodeMessage(MovieTimecode):
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
