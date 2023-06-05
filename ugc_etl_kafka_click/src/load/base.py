from clickhouse_driver import Client, errors
from .schema import ClickhouseBulkData
from core.config import settings
import backoff

from logging import getLogger
logger = getLogger(__name__)


class ClickhouseLoader:
    def __init__(self, host: str) -> None:
        self.host = host
        self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._client and self._client.connection.connected:
                self.client.disconnect()
        except Exception:
            logger.exception(
                'Возникла ошибка при закрытии соединения Clickouse, host=%s', self.host
            )

    @property
    def client(self) -> Client:
        if not self._client or not self._client.connection.connected:
            self._client = Client(self.host)
        return self._client

    @backoff.on_exception(backoff.expo,
                          (errors.NetworkError, ConnectionRefusedError),
                          max_time=settings.backoff_max_time)
    def load(self, transformed_data: ClickhouseBulkData) -> None:
        logger.info('Loading data %s rows', transformed_data.count)
        self.client.execute(transformed_data.query)
