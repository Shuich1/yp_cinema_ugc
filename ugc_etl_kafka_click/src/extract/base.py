from logging import getLogger
from typing import Generator
from kafka import KafkaConsumer
from .schema import KafkaData, KafkaBulkData
from functools import cached_property
from core.config import settings
import orjson
import backoff


logger = getLogger(__name__)


class KafkaExtractor:
    def __init__(self, topic: str, server: str, group_id: str) -> None:
        self.topic = topic
        self.server = server
        self.group_id = group_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if 'consumer' in self.__dict__:
                self.consumer.close(autocommit=False)
        except Exception:
            logger.exception('Возникла ошибка при закрытии соединения Kafka, server=%s', self.server)

    @cached_property
    @backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=settings.BACKOFF_MAX_TIME)
    def consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            self.topic,
            bootstrap_servers=[self.server],
            auto_offset_reset='earliest',
            group_id=self.group_id,
            value_deserializer=orjson.loads,
            enable_auto_commit=False,
            consumer_timeout_ms=1000
        )

    @backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=settings.BACKOFF_MAX_TIME)
    def get_updates(self) -> Generator[KafkaBulkData | None, None, None]:
        while True:
            result = KafkaBulkData(payload=[])
            response = self.consumer.poll(update_offsets=False, timeout_ms=1000)
            for records in response.values():
                for record in records:
                    try:
                        kafka_data = KafkaData(**record.value)
                    except Exception:
                        logger.warning('Пропуск записи %s. Неверный формат', record.value)
                    else:
                        result.payload.append(kafka_data)
            yield result
            self.consumer.commit()
