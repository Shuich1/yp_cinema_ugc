from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient

client: AsyncIOMotorClient | None = None


@lru_cache
async def get_mongo_client() -> AsyncIOMotorClient:
    return client
