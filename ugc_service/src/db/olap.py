from abc import ABC, abstractmethod
from core.config import settings
from typing import Optional
from asynch import connect
import backoff


class GenericOlap(ABC):
    pass

    @abstractmethod
    async def disconnect(self):
        pass


class ClickHouseOlap(GenericOlap):
    def __init__(self, bootstrap_servers: list) -> None:
        self.bootstrap_servers = bootstrap_servers

    @backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=settings.BACKOFF_MAX_TIME)   
    async def connect(self) -> None:
        self.connection = await connect(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOSE_PORT,
            database=settings.CLICKHOUSE_DB,
            # user = "default",
            # password = "",
        )

    async def _execute(self, query) -> str:
        async with self.connection.cursor() as cursor:
            await cursor.execute(query)
            return cursor
    
    async def disconnect(self) -> None:
        await self.producer.stop()




olap_bd: Optional[GenericOlap] = None


async def get_olap() -> GenericOlap:
    return olap_bd
