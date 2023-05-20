import time
from functools import wraps
from itertools import chain, islice
from typing import Callable, Iterable, Iterator


def duplicate_first_row(gen_func: Callable) -> Callable:
    @wraps(gen_func)
    def decorator(*args, **kwargs):
        generator = gen_func(*args, **kwargs)
        first_row = next(generator)
        yield from chain([first_row] * 2, generator)

    return decorator


def split_into_chunks(iterable: Iterable, size: int) -> Iterator[list]:
    iterator = iter(iterable)
    while chunk := list(islice(iterator, size)):
        yield chunk


def measure_time(func: Callable, *args, repeats: int = 1, **kwargs) -> float:
    start_time = time.perf_counter()
    for _ in range(repeats):
        func(*args, **kwargs)
    end_time = time.perf_counter()
    return (end_time - start_time) / repeats
