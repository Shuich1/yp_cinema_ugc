import pytest
import requests
from pymongo import MongoClient

from settings import settings
from utils import get_jtw_token


@pytest.fixture(scope='session')
def http_session():
    session = requests.session()
    yield session
    session.close()


@pytest.fixture
def api_request(http_session):
    def inner(endpoint_method, endpoint_url, user_id=None, **kwargs):
        url = settings.api_url + endpoint_url
        request_kwargs = {'method': endpoint_method, 'url': url, **kwargs}
        if user_id:
            token = get_jtw_token(user_id)
            request_kwargs.update(headers={'Authorization': f'Bearer {token}'})
        return http_session.request(**request_kwargs)

    return inner


@pytest.fixture(scope='session')
def mongo_client():
    client = MongoClient(
        host=settings.mongodb_host,
        port=settings.mongodb_port,
        uuidRepresentation='standard',
    )
    yield client
    client.close()


@pytest.fixture
def db(mongo_client):
    mongo_client.drop_database('films')
    return mongo_client.get_database('films')
