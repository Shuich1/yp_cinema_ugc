import logging
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError
from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class ProducerError(Exception):
    pass


class Producer(ABC):
    @abstractmethod
    async def on_startup(self) -> None:
        pass

    @abstractmethod
    async def on_shutdown(self) -> None:
        pass

    @abstractmethod
    async def push(self, key: str, value: str) -> None:
        pass


class KafkaSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=9092)
    topic_name: str = Field(default='timecodes')
    num_partitions: int = Field(default=1)
    replication_factor: int = Field(default=1)

    class Config:
        env_prefix = 'kafka_'


class KafkaProducer(Producer):
    def __init__(self):
        self.settings = KafkaSettings()
        self.kafka = None

    async def on_startup(self) -> None:
        broker_addr = f'{self.settings.host}:{self.settings.port}'
        try:
            await self._check_topic_exists()
        except KafkaError as ex:
            logger.error(ex)
            raise ProducerError()

        self.kafka = AIOKafkaProducer(bootstrap_servers=[broker_addr])
        await self.kafka.start()

    async def _check_topic_exists(self) -> None:
        broker_addr = f'{self.settings.host}:{self.settings.port}'
        admin = AIOKafkaAdminClient(bootstrap_servers=[broker_addr])
        await admin.start()

        if self.settings.topic_name not in await admin.list_topics():
            topic = NewTopic(
                self.settings.topic_name,
                num_partitions=self.settings.num_partitions,
                replication_factor=self.settings.replication_factor,
            )
            await admin.create_topics([topic])
        await admin.close()

    async def on_shutdown(self) -> None:
        await self.kafka.stop()

    async def push(self, key: str, value: str) -> None:
        try:
            await self.kafka.send_and_wait(
                self.settings.topic_name,
                value=bytes(value, encoding='utf-8'),
                key=bytes(key, encoding='utf-8'),
            )
        except KafkaError as ex:
            logger.error(ex)
            raise ProducerError()
