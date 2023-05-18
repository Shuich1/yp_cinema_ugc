import random
import uuid
from datetime import datetime
from typing import Iterator

from utils import duplicate_first_row


@duplicate_first_row
def test_data(rows_count: int) -> Iterator[tuple]:
    films_count = int(rows_count / 1000) or 1
    film_ids = [str(uuid.uuid4()) for _ in range(films_count)]

    users_count = int(rows_count / 100) or 1
    user_ids = [str(uuid.uuid4()) for _ in range(users_count)]

    film_length = 60 * 60 * 3

    event_time_range = (
        datetime(2020, 1, 1).timestamp(),
        datetime(2023, 1, 1).timestamp(),
    )

    for _ in range(rows_count):
        start_time = random.randint(0, film_length)
        yield (
            random.choice(film_ids),
            random.choice(user_ids),
            start_time,
            start_time + 10,
            datetime.fromtimestamp(random.randint(*event_time_range)),
        )
