from collections import OrderedDict
from typing import Literal, Callable

from fastapi import Query


def get_sorting_params(fields: list[str], *, default: str | None = None) -> Callable:
    options = tuple(f'{f}:{o}' for f in fields for o in ('asc', 'desc'))

    def sorting_params(
            sort: list[Literal[options]] | None = Query([default])  # noqa
    ) -> OrderedDict[str, str]:

        parsed_params = OrderedDict()
        for param in sort:
            field, order = param.split(':')
            if field not in parsed_params:
                parsed_params.update({field: order})
        return parsed_params

    return sorting_params
