from datetime import datetime
from uuid import UUID

from models.base import BaseModel
from pydantic import Field


class Bookmark(BaseModel):
    film_id: UUID
    user_id: UUID
    created: datetime = Field(default_factory=datetime.utcnow)
