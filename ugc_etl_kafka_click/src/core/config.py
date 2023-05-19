import os
from pydantic import BaseSettings, Field
from logging import getLogger, basicConfig

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, 'core', '.env')


class Settings(BaseSettings):
    KAFKA_TOPIC: str = Field(..., env='KAFKA_TOPIC')
    KAFKA_SERVER: str = Field(..., env='KAFKA_SERVER')
    KAFKA_GROUPID: str = Field(..., env='KAFKA_GROUPID')
    CLICKHOUSE_HOST: str = Field(..., env='CLICKHOUSE_HOST')
    CLICKHOUSE_TABLENAME: str = Field(..., env='CLICKHOUSE_TABLENAME')
    BACKOFF_MAX_TIME: float = Field(..., env='BACKOFF_MAX_TIME')
    SLEEP_INTERVAL: int = Field(..., env='SLEEP_INTERVAL')

    class Config:
        env_file = ENV_FILE_PATH


settings = Settings()

FORMAT = '%(asctime)s | %(levelname)-9s | %(name)s | %(message)s'
basicConfig(format=FORMAT)
getLogger().setLevel('INFO')
