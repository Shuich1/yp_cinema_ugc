from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Bookmark(BaseModel):
    film_id: UUID = Field(default_factory=uuid4)
    user_id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.utcnow)

    @property
    def id(self) -> tuple[str, str]:
        return str(self.film_id), str(self.user_id)
