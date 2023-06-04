from pydantic import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str
    mongodb_uri: str


settings = Settings()
