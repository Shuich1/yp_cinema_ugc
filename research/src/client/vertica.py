from contextlib import contextmanager
from typing import Generator, Iterable

import backoff
import vertica_python

from utils import split_into_chunks
from .base import DBClient


class VerticaClient(DBClient):
    dbms_name = 'Vertica'

    def __init__(self, **connection_info):
        self.connection_info = connection_info
        self.connection = None

    @contextmanager
    def connect(self) -> Generator:
        try:
            self.connection = self._acquire_connection()
            yield
        finally:
            hasattr(self.connection, 'close') and self.connection.close()

    @backoff.on_exception(backoff.expo,
                          exception=vertica_python.errors.ConnectionError,
                          max_time=60,
                          max_value=2)
    def _acquire_connection(self) -> vertica_python.Connection:
        return vertica_python.connect(**self.connection_info)

    def prepare_database(self) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS timecodes')
            cursor.execute('''
                CREATE TABLE timecodes (
                    film_id VARCHAR(36),
                    user_id VARCHAR(36),
                    start_time INTEGER,
                    end_time INTEGER,
                    event_time DATETIME
                )
            ''')

    def retrieve_last_timecode(self, film_id: str, user_id: str) -> None:
        query = '''
            SELECT end_time
            FROM timecodes
            WHERE film_id = %s
              AND user_id = %s
            ORDER BY event_time DESC
            LIMIT 1
        '''
        with self.connection.cursor() as cursor:
            cursor.execute(query, (film_id, user_id))
            cursor.fetchone()

    def retrieve_most_viewed(self, films_count: int = 10) -> None:
        query = '''
            SELECT film_id, COUNT(*) AS views
            FROM timecodes
            GROUP BY film_id
            ORDER BY views DESC
            LIMIT %s
        '''
        with self.connection.cursor() as cursor:
            cursor.execute(query, (films_count,))
            cursor.fetchall()

    def insert_data(self, data: Iterable[tuple]) -> None:
        query = '''
            INSERT INTO timecodes (
                film_id,
                user_id,
                start_time,
                end_time,
                event_time
            )
            VALUES (%s, %s, %s, %s, %s)
        '''
        with self.connection.cursor() as cursor:
            for chunk in split_into_chunks(data, 10_000):
                cursor.executemany(query, chunk)
