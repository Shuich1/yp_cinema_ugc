import threading
import time
from dataclasses import dataclass
from queue import Queue
from typing import Iterable, Iterator

from client.base import DBClient
from data import test_data
from utils import measure_time

log_template = '''
DBMS:                                    {0}
- Insert 100k rows:                      {1:.6f} s
- Retrieve last timecode:                {2:.6f} s
- Retrieve most viewed films:            {3:.6f} s
- Retrieve last timecode under load:     {4:.6f} s
- Retrieve most viewed films under load: {5:.6f} s
'''


@dataclass
class TestResult:
    dbms_name: str
    insert_100k_rows: float
    retrieve_last_timecode: float
    retrieve_most_viewed: float
    retrieve_last_timecode_under_load: float
    retrieve_most_viewed_under_load: float

    @property
    def log_message(self):
        return log_template.format(
            self.dbms_name,
            self.insert_100k_rows,
            self.retrieve_last_timecode,
            self.retrieve_most_viewed,
            self.retrieve_last_timecode_under_load,
            self.retrieve_most_viewed_under_load,
        )


class TestSuite:
    def __init__(self, rows_count: int, wps: int):
        self.clients = []
        self.queue = Queue()
        self.rows_count = rows_count
        self.wps = wps
        self.stress_tests_finished = False

    def register(self, client: DBClient) -> None:
        self.clients.append(client)

    def run(self):
        for client in self.clients:
            initial_data = test_data(self.rows_count)
            film_id, user_id, *_ = next(initial_data)

            static_tests_result = self.run_static_tests(
                client,
                initial_data,
                film_id,
                user_id,
            )
            stress_tests_result = self.run_stress_tests(
                client,
                film_id,
                user_id,
            )

            yield TestResult(
                dbms_name=client.dbms_name,
                **static_tests_result,
                **stress_tests_result,
            )

    @staticmethod
    def run_static_tests(client: DBClient,
                         initial_data: Iterable[tuple],
                         film_id: str,
                         user_id: str,
                         ) -> dict[str, float]:
        with client.connect():
            client.prepare_database()
            client.insert_data(initial_data)

            time.sleep(1)  # Give dbms some time to update indices
            data = list(test_data(100_000))
            t1 = measure_time(client.insert_data, data)

            time.sleep(1)
            t2 = measure_time(
                client.retrieve_last_timecode,
                film_id, user_id,
                repeats=100,
            )
            t3 = measure_time(client.retrieve_most_viewed, repeats=100)

        return {
            'insert_100k_rows': t1,
            'retrieve_last_timecode': t2,
            'retrieve_most_viewed': t3,
        }

    def run_stress_tests(self,
                         client: DBClient,
                         film_id: str,
                         user_id: str,
                         ) -> dict[str, float]:
        max_producing_time = 10
        data = test_data(max_producing_time * self.wps)

        producer_thread = threading.Thread(
            target=self.produce,
            args=(data, 1 / self.wps),
        )
        consumer_thread = threading.Thread(
            target=self.consume,
            args=(client.copy(),)
        )

        self.stress_tests_finished = False
        producer_thread.start()
        consumer_thread.start()

        time.sleep(1)  # Let producer and consumer threads begin working
        with client.connect():
            t1 = measure_time(
                client.retrieve_last_timecode,
                film_id, user_id,
                repeats=100,
            )
            t2 = measure_time(client.retrieve_most_viewed, repeats=100)

        self.stress_tests_finished = True

        return {
            'retrieve_last_timecode_under_load': t1,
            'retrieve_most_viewed_under_load': t2,
        }

    def produce(self, data: Iterable[tuple], period: float) -> None:
        next_produce = time.time()

        for row in data:
            if self.stress_tests_finished:
                break

            self.queue.put_nowait(row)

            next_produce += period
            sleep_time = next_produce - time.time()
            time.sleep(sleep_time > 0 and sleep_time or 0)

        self.queue.put(None)

    def consume(self, client: DBClient) -> None:
        with client.connect():
            client.insert_data(data=self.iter_queue())

    def iter_queue(self) -> Iterator[tuple]:
        while True:
            row = self.queue.get()
            if row is None:
                return
            yield row
