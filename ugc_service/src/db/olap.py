from abc import ABC, abstractmethod
from typing import Optional


class GenericOlap(ABC):
    pass

    @abstractmethod
    async def disconnect(self):
        pass


olap_bd: Optional[GenericOlap] = None


async def get_olap() -> GenericOlap:
    return olap_bd
