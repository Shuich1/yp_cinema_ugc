import sys
import os
import random
import uuid
from datetime import datetime
from typing import Iterator


# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import duplicate_first_row


@duplicate_first_row
def test_data(rows_count: int) -> Iterator[tuple]:
    films_count = int(rows_count / 1000) or 1
    film_ids = [str(uuid.uuid4()) for _ in range(films_count)]

    users_count = int(rows_count / 100) or 1
    user_ids = [str(uuid.uuid4()) for _ in range(users_count)]

    event_time_range = (
        int(datetime(2020, 1, 1).timestamp()),
        int(datetime(2023, 1, 1).timestamp()),
    )

    for _ in range(rows_count):
        score = random.randint(1, 10)
        yield (
            random.choice(film_ids),
            random.choice(user_ids),
            datetime.fromtimestamp(random.randint(*event_time_range)),
            score,
        )
