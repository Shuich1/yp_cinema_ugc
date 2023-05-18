import logging.config
from pathlib import Path

import yaml
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent
    log_level: str = Field(default='debug', env='ugc_api_log_level')

    jwt_secret: str = Field(default='secret')
    jwt_algorithm: str = Field(default='HS256')

    @property
    def log_config(self):
        return str(self.base_dir / 'core/logging.yml')


def configure_logging(log_config: str):
    with open(log_config) as file:
        logging.config.dictConfig(yaml.load(file, yaml.FullLoader))


settings = Settings()
