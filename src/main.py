import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from api.v1 import ratings, reviews, bookmarks
from core.config import settings
from db import mongo

app = FastAPI()

app.include_router(ratings.router)
app.include_router(reviews.router)
app.include_router(bookmarks.router)


@app.on_event('startup')
async def on_startup():
    mongo.client = AsyncIOMotorClient(
        settings.mongodb_uri,
        uuidRepresentation='standard',
    )


@app.on_event('shutdown')
async def on_shutdown():
    mongo.client.close()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
    )
