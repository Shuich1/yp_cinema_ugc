from contextlib import contextmanager
from typing import Generator, Iterable

import backoff
from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError

from utils import split_into_chunks
from .base import DBClient


class ClickHouseClient(DBClient):
    dbms_name = 'ClickHouse'

    def __init__(self, **connection_info):
        self.connection_info = connection_info
        self.client = None

    @contextmanager
    def connect(self) -> Generator:
        try:
            self.client = Client(**self.connection_info)
            self._check_connection()
            yield
        finally:
            self.client.disconnect()

    @backoff.on_exception(backoff.expo,
                          exception=NetworkError,
                          max_time=60,
                          max_value=2)
    def _check_connection(self) -> None:
        self.client.execute('SELECT 1')

    def prepare_database(self) -> None:
        self.client.execute('CREATE DATABASE IF NOT EXISTS movies')
        self.client.execute('DROP TABLE IF EXISTS movies.timecodes')
        self.client.execute('''
            CREATE TABLE movies.timecodes (
                film_id String,
                user_id String,
                start_time UInt16,
                end_time UInt16,
                event_time DateTime
            )
            ENGINE = MergeTree()
            ORDER BY (film_id, user_id)
        ''')

    def retrieve_last_timecode(self, film_id: str, user_id: str) -> None:
        query = '''
            SELECT end_time
            FROM movies.timecodes
            WHERE film_id = %(film_id)s
              AND user_id = %(user_id)s
            ORDER BY event_time DESC
            LIMIT 1
        '''
        self.client.execute(query, {'film_id': film_id, 'user_id': user_id})

    def retrieve_most_viewed(self, films_count: int = 10) -> None:
        query = '''
            SELECT film_id, count(*) AS views
            FROM movies.timecodes
            GROUP BY film_id
            ORDER BY views DESC
            LIMIT %(films_count)s
        '''
        self.client.execute(query, {'films_count': films_count})

    def insert_data(self, data: Iterable[tuple]) -> None:
        query = '''
            INSERT INTO movies.timecodes (
                film_id,
                user_id,
                start_time,
                end_time,
                event_time
            )
            VALUES
        '''
        for chunk in split_into_chunks(data, 10_000):
            self.client.execute(query, chunk)
