from abc import ABC, abstractmethod
from contextlib import contextmanager
from copy import copy
from typing import ContextManager, Iterable


class DBClient(ABC):
    dbms_name: str

    @contextmanager
    def connect(self) -> ContextManager:
        yield

    def copy(self):
        return copy(self)

    @abstractmethod
    def prepare_database(self) -> None:
        pass

    @abstractmethod
    def retrieve_last_timecode(self, film_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    def retrieve_most_viewed(self, films_count: int = 10) -> None:
        pass

    @abstractmethod
    def insert_data(self, data: Iterable[tuple]) -> None:
        pass
