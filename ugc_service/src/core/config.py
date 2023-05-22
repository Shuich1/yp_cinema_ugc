import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, 'core', '.env')


class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    BACKOFF_MAX_TIME: int

    # Настройки Uvicorn
    UVICORN_APP_NAME: str
    UVICORN_HOST: str
    UVICORN_PORT: int

    # Настройки Kafka
    KAFKA_HOST: str
    KAFKA_PORT: int
    KAFKA_VIEW_TOPIC: str

    # Настройки ClickHouse
    CLICKHOUSE_HOST: str
    CLICKHOSE_PORT: str

    class Config:
        env_file = ENV_FILE_PATH


logging_config.dictConfig(LOGGING)

settings = Settings()
