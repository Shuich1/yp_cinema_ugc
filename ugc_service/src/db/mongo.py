from functools import lru_cache
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

client: Optional[AsyncIOMotorClient] = None


@lru_cache # type: ignore
async def get_mongo_client() -> AsyncIOMotorClient:
    return client
