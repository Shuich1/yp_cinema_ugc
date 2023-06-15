import os
import pymongo
from contextlib import contextmanager
from typing import ContextManager, Iterable

from .base import DBClient


class MongoDBClient(DBClient):
    dbms_name = "MongoDB"
    db_name = os.environ.get("MONGO_INITDB_DATABASE", "movie_db_usg_9_test")

    def __init__(self, **connection_info):
        self.connection_info = connection_info
        self.connection = self._acquire_connection()

    @contextmanager
    def connect(self) -> ContextManager:
        try:
            yield self.connection
        finally:
            pass

    def _acquire_connection(self):
        return pymongo.MongoClient(**self.connection_info)

    def close_connection(self):
        self.connection and self.connection.close()

    def prepare_database(self) -> None:
        with self.connect() as connection:
            # Access the collection
            likes_collection = connection[self.db_name].likes

            # Check if the index exists
            indexes = likes_collection.list_indexes()
            index_exists = any(index["key"].get("film_id") and index["key"].get("user_id") for index in indexes)

            # If index exists, delete all documents from the collection
            if index_exists:
                likes_collection.delete_many({})

            # Create the index (will not recreate if already exists)
            likes_collection.create_index([("film_id", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], unique=True)

    def insert_data(self, data: Iterable[tuple]) -> None:
        with self.connect() as connection:
            db = connection[self.db_name]

            # Iterate through each data entry
            for film_id, user_id, event_time, score in data:
                # Define the filter for existing document
                filter = {"film_id": film_id, "user_id": user_id}

                # Define the data to be updated/inserted
                new_data = {"$set": {"event_time": event_time, "score": score}}

                # Use update_one with upsert option
                db.likes.update_one(filter, new_data, upsert=True)

    def retrieve_last_timecode(self, film_id: str, user_id: str):
        pass

    def retrieve_most_viewed(self, films_count: int = 10) -> None:
        pass

    def retrieve_numbers_of_likes(self, film_id: str):
        with self.connect() as connection:
            db = connection[self.db_name]
            return db.likes.count_documents({"film_id": film_id})

    def retrieve_average_score_for_movie(self, film_id: str):
        with self.connect() as connection:
            db = connection[self.db_name]
            result = db.likes.aggregate(
                [{"$match": {"film_id": film_id}}, {"$group": {"_id": "$film_id", "average_score": {"$avg": "$score"}}}]
            )
            result_list = list(result)
            return result_list[0]["average_score"] if result_list else None
