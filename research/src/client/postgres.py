import psycopg2
from contextlib import contextmanager
from typing import Generator, Iterable, Optional, Any

from utils import split_into_chunks
from .base import DBClient


class PostgresClient(DBClient):
    dbms_name = "PostgreSQL"

    def __init__(self, **connection_info) -> None:
        self.connection_info = connection_info

    @contextmanager
    def connect(self) -> Generator[psycopg2.extensions.connection, None, None]:
        connection = self._acquire_connection()
        try:
            yield connection
        finally:
            connection and connection.close()

    def _acquire_connection(self):
        return psycopg2.connect(**self.connection_info)

    def prepare_database(self) -> None:
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS likes")
                cursor.execute(
                    """
                    CREATE TABLE likes (
                        film_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        event_time TIMESTAMP,
                        score smallint NOT NULL,
                        PRIMARY KEY (film_id, user_id)
                    )
                """
                )
                connection.commit()

    def insert_data(self, data: Iterable[tuple]) -> None:
        query = """
            INSERT INTO likes (film_id, user_id, event_time, score)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (film_id, user_id) DO UPDATE SET
                event_time = excluded.event_time;
        """
        with self.connect() as connection:
            with connection.cursor() as cursor:
                for chunk in split_into_chunks(data, 10_000):
                    cursor.executemany(query, chunk)
                connection.commit()

    def retrieve_last_timecode(
        self, film_id: str, user_id: str
    ) -> Optional[Any]:
        query = """
            SELECT event_time
            FROM likes
            WHERE film_id = %s
            AND user_id = %s
            ORDER BY event_time DESC
            LIMIT 1
        """
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (film_id, user_id))
                result = cursor.fetchone()
                return result[0] if result else None

    def retrieve_most_viewed(self, films_count: int = 10) -> None:
        pass

    def retrieve_numbers_of_likes(self, film_id: str) -> Optional[Any]:
        query = """
                SELECT film_id, COUNT(*) as number_of_likes
                FROM likes
                WHERE film_id = %s
                GROUP BY film_id
        """
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (film_id,))
                result = cursor.fetchone()
                return result[0] if result else None

    def retrieve_average_score_for_movie(
        self, film_id: str
    ) -> Optional[float]:
        query = """
                SELECT AVG(score) as average_score
                FROM likes
                WHERE film_id = %s;
        """
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (film_id,))
                result = cursor.fetchone()
                return result[0] if result else None
