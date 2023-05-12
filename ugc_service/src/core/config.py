import os
from logging import config as logging_config
from core.logger import LOGGING
from pydantic import BaseSettings, Field


# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, 'core', '.env')


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(..., env='PROJECT_NAME')
    PROJECT_DESCRIPTION: str = Field(..., env='PROJECT_DESCRIPTION')

    # Настройки Uvicorn
    UVICORN_APP_NAME: str = Field(..., env='UVICORN_APP_NAME')
    UVICORN_HOST: str = Field(..., env='UVICORN_HOST')
    UVICORN_PORT: int = Field(..., env='UVICORN_PORT')

    class Config:
        env_file = ENV_FILE_PATH


logging_config.dictConfig(LOGGING)

settings = Settings()
