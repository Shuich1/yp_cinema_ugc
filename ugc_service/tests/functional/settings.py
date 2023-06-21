from pydantic import BaseSettings
from requests.compat import urljoin


class Settings(BaseSettings):
    api_host: str = 'localhost'
    api_port: int = 8000
    api_path: str = '/ugc/api/v1'

    mongodb_host: str = 'localhost'
    mongodb_port: int = 27017

    jwt_secret_key: str = 'test'

    @property
    def api_url(self):
        base_url = f'http://{self.api_host}:{self.api_port}'
        return urljoin(base_url, self.api_path)


settings = Settings()
