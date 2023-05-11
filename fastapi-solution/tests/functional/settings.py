from pydantic import BaseSettings, Field

from .testdata.es_mapping import index_mappings, index_settings


class TestSettings(BaseSettings):
    es_url: str = Field('http://elastic_test:9200', env='ES_TEST_URL')
    es_id_field: str = Field('id', env='ES_ID_FIELD')
    es_index_mappings: dict = Field(index_mappings)
    es_index_settings: dict = Field(index_settings)

    redis_host: str = Field('redis_test', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')

    service_url: str = Field('http://127.0.0.1:80', env='FASTAPI_URL')


test_settings = TestSettings()
