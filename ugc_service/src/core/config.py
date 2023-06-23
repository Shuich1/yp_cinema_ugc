import os
from logging import config as logging_config
from contextvars import ContextVar

from core.logger import LOGGING
from pydantic import BaseSettings

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, 'core', '.env')


class Settings(BaseSettings):
    project_name: str
    project_description: str
    backoff_max_time: int

    # Настройки Uvicorn
    uvicorn_app_name: str
    uvicorn_host: str
    uvicorn_port: int

    # Настройки Kafka
    kafka_host: str
    kafka_port: int
    kafka_view_topic: str

    # Настройки ClickHouse
    clickhouse_host: str
    clickhouse_port: str

    # Auth
    authjwt_secret_key: str

    # MongoDB settings
    mongodb_uri: str

    # Sentry
    sentry_enabled: bool = True
    sentry_dsn: str | None = None

    class Config:
        env_file = ENV_FILE_PATH


logging_config.dictConfig(LOGGING)

settings = Settings()
