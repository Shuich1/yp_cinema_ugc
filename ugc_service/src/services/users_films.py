from functools import lru_cache

from fastapi import Depends

from db.olap import get_olap, GenericOlap
from db.oltp import get_oltp, GenericOltp
from models.users_films import UserFilmTimestamp
from datetime import datetime
from uuid import UUID


class UserFilmService:
    def __init__(self, olap: GenericOlap, oltp: GenericOltp):
        self.olap = olap
        self.oltp = oltp
    
    def create_user_film_timestamp(self, user_id: UUID, film_id: UUID, start_time: int, end_time: int, timestamp: datetime):
        # TODO
        pass


@lru_cache()
def get_userfilm_service(
        olap: GenericOlap = Depends(get_olap),
        oltp: GenericOltp = Depends(get_oltp),
) -> UserFilmService:
    return UserFilmService(olap, oltp)
