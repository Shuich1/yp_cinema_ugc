from datetime import datetime
from uuid import UUID

from models.base import BaseModel


class UserFilmTimestamp(BaseModel):
    user_id: UUID
    film_id: UUID
    start_time: int
    end_time: int
    timestamp: datetime
