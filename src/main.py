import uvicorn
from fastapi import FastAPI
from api.v1 import ratings, reviews, bookmarks
from db import mongo
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
app.include_router(ratings.router)
app.include_router(reviews.router)
app.include_router(bookmarks.router)


@app.on_event('startup')
async def on_startup():
    mongo.client = AsyncIOMotorClient(
        'mongodb://127.0.0.1:27017',
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
