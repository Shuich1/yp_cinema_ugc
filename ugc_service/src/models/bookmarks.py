from datetime import datetime
from uuid import UUID

from pydantic import Field

from models.base import BaseModel


class Bookmark(BaseModel):
    film_id: UUID
    user_id: UUID
    created: datetime = Field(default_factory=datetime.utcnow)
