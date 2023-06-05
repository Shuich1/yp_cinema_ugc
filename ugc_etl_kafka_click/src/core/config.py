import os
from pydantic import BaseSettings
from logging import getLogger, basicConfig

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, 'core', '.env')


class Settings(BaseSettings):
    kafka_topic: str
    kafka_server: str
    kafka_groupid: str
    clickhouse_host: str
    clickhouse_tablename: str
    backoff_max_time: float
    sleep_interval: int

    class Config:
        env_file = ENV_FILE_PATH


settings = Settings()

FORMAT = '%(asctime)s | %(levelname)-9s | %(name)s | %(message)s'
basicConfig(format=FORMAT)
getLogger().setLevel('INFO')
