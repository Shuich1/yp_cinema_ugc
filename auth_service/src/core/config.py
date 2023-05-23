import os

from pydantic import BaseSettings, Field

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_file = '.env'
ENV_FILE_PATH = os.path.join(BASE_DIR, 'core', env_file)


class Settings(BaseSettings):
    # Общие настройки
    debug: bool = Field(..., env='DEBUG')
    enable_tracer: bool = Field(..., env='ENABLE_TRACER')
    base_dir: str = Field(BASE_DIR)
    base_uri: str = Field(..., env='BASE_URI')
    request_limit: int = Field(..., env='REQUEST_LIMIT_PER_MINUTE')

    # Настройки приложения
    app_name: str = Field(..., env='APP_NAME')
    app_host: str = Field(..., env='APP_HOST')
    app_port: int = Field(..., env='APP_PORT')
    app_secret_key: str = Field(..., env='APP_SECRET_KEY')
    app_debug_level: str = Field(..., env='APP_DEBUG_LEVEL')

    # Настройки СУБД
    db_ms: str = Field(..., env='DB_MS')
    db_host: str = Field(..., env='DB_HOST')
    db_port: int = Field(..., env='DB_PORT')
    db_name: str = Field(..., env='DB_NAME')
    db_user: str = Field(..., env='DB_USER')
    db_pwd: str = Field(..., env='DB_PWD')

    # Настройки Redis
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')

    # Настройки JWT
    jwt_sectet_key: str = Field(..., env='JWT_SECRET_KEY')
    jwt_access_token_expires: int = Field(..., env='JWT_ACCESS_TOKEN_EXPIRES')
    jwt_refresh_token_expires: int = Field(..., env='JWT_REFRESH_TOKEN_EXPIRES')

    # Настройки oauth
    rel_google_client_secret_file: str = Field(..., env='GOOGLE_CLIENT_SECRETS_FILE')
    vk_client_id: str = Field(..., env='VK_CLIENT_ID')
    vk_client_secret: str = Field(..., env='VK_CLIENT_SECRET')
    yandex_client_id: str = Field(..., env='YANDEX_CLIENT_ID')
    yandex_client_secret: str = Field(..., env='YANDEX_CLIENT_SECRET')
    mailru_client_id: str = Field(..., env='MAILRU_CLIENT_ID')
    mailru_client_secret: str = Field(..., env='MAILRU_CLIENT_SECRET')

    # Настройки jaeger
    jaeger_agent_host: str = Field(..., env='JAEGER_AGENT_HOST')
    jaeger_agent_port: str = Field(..., env='JAEGER_AGENT_PORT')

    # Суперюзер
    admin_login: str = Field(..., env='APP_ADMIN_LOGIN')
    admin_password: str = Field(..., env='APP_ADMIN_PASSWORD')

    class Config:
        env_file = ENV_FILE_PATH


settings = Settings()
