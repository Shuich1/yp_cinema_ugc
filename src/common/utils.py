from typing import Literal, Callable

from fastapi import Query


def get_page_params(default_limit: int = 10, max_limit: int = 100) -> Callable:
    def page_params(
            offset: int | None = Query(0, ge=0),
            limit: int | None = Query(default_limit, ge=0, le=max_limit),
    ) -> dict[str, int]:
        return {'offset': offset, 'limit': limit}

    return page_params


def get_sorting_params(fields: list[str], *, default: str | None = None) -> Callable:
    options = tuple(f'{f}:{o}' for f in fields for o in ('asc', 'desc'))

    def sorting_params(
            sort: list[Literal[options]] | None = Query([default])  # noqa
    ) -> dict:

        parsed_params = {}
        for param in sort:
            field, order = param.split(':')
            if field not in parsed_params:
                parsed_params.update({field: order})
        return parsed_params

    return sorting_params
