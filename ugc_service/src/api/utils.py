from typing import Callable, Dict, List, Optional
from typing_extensions import Literal

from fastapi import Query


def get_page_params(default_limit: int = 10, max_limit: int = 100) -> Callable:
    def page_params(
            offset: Optional[int] = Query(0, ge=0),
            limit: Optional[int] = Query(default_limit, ge=0, le=max_limit),
    ) -> Dict[str, Optional[int]]:
        return {'offset': offset, 'limit': limit}

    return page_params


def get_sorting_params(fields: List[str],
                       *,
                       default: Optional[str] = None,
                       ) -> Callable:
    options = tuple(f'{f}:{o}' for f in fields for o in ('asc', 'desc'))

    def sorting_params(
            sort: List[Literal[options]] = Query([default]) # type: ignore # noqa
    ) -> dict:

        parsed_params = {}
        for param in sort:
            field, order = param.split(':')
            if field not in parsed_params:
                parsed_params.update({field: order})
        return parsed_params

    return sorting_params
