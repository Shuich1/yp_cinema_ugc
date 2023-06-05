from pydantic import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str
    authjwt_secret_key: str


settings = Settings()
