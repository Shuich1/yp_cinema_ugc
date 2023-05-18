from clickhouse_driver import Client
from functools import cached_property
from .schema import ClickhouseBulkData
from core.config import settings
import backoff

from logging import getLogger
logger = getLogger(__name__)


class ClickhouseLoader:
    def __init__(self, host: str) -> None:
        self.host = host

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if 'client' in self.__dict__:
                self.client.disconnect()
        except Exception:
            logger.exception('Возникла ошибка при закрытии соединения Clickouse, host=%s', self.host)

    @cached_property
    @backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=settings.BACKOFF_MAX_TIME)
    def client(self) -> Client:
        return Client(
            self.host,
        )

    @backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=settings.BACKOFF_MAX_TIME)
    def load(self, transformed_data: ClickhouseBulkData) -> None:
        logger.info('Loading data %s rows', transformed_data.count)
        self.client.execute(transformed_data.query)
