from abc import ABC, abstractmethod
from core.config import settings
from typing import Optional
from asynch import connect
from asynch.cursors import DictCursor
from models.users_films import UserFilmTimestamp
from uuid import UUID
import backoff


class GenericOlap(ABC):
    pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def get_last_user_film_timestamp(self, user_id: UUID, film_id: UUID) -> UserFilmTimestamp:
        pass


class ClickHouseOlap(GenericOlap):
    def __init__(self, host: str, port: str) -> None:
        self.host = host
        self.port = port
        self._connect = None

    @backoff.on_exception(backoff.expo, Exception, max_time=settings.BACKOFF_MAX_TIME)
    async def connect(self) -> None:
        self._connect = await connect(
            host=self.host,
            port=self.port,
        )

    @backoff.on_exception(backoff.expo, Exception, max_time=settings.BACKOFF_MAX_TIME)
    async def get_last_user_film_timestamp(self, user_id: UUID, film_id: UUID) -> UserFilmTimestamp | None:
        async with self._connect.cursor(cursor=DictCursor) as cursor:
            count = await cursor.execute("""
                SELECT * FROM default.view
                WHERE (user_id=='{user_id}') AND (film_id=='{film_id}')
                ORDER BY event_time DESC LIMIT 1
            """.format(user_id=user_id, film_id=film_id))
            if not count:
                return None
            result = await cursor.fetchone()
            return UserFilmTimestamp(
                user_id=result['user_id'],
                film_id=result['film_id'],
                start_time=result['start_time'],
                end_time=result['end_time'],
                timestamp=result['event_time']
            )

    async def disconnect(self) -> None:
        await self.producer.stop()


olap_bd: Optional[GenericOlap] = None


async def get_olap() -> GenericOlap:
    return olap_bd
