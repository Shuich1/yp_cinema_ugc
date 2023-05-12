from typing import Optional
from abc import ABC, abstractmethod


class GenericOltp(ABC):
    pass

    @abstractmethod
    async def disconnect(self):
        pass


oltp_bd: Optional[GenericOltp] = None


async def get_oltp() -> GenericOltp:
    return oltp_bd
