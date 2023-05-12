import orjson

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UserFilmTimestamp(BaseModel):
    user_id: UUID
    film_id: UUID
    start_time: int
    end_time: int
    timestamp: datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
