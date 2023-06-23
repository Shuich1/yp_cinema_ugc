from logging import getLogger
from contextlib import asynccontextmanager

import uvicorn
import sentry_sdk

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from core.config import settings
from core.logger import LOGGING
from db import mongo, olap, oltp
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from api.v1 import users_films, ratings, reviews, bookmarks
from core.config import settings
from core.middleware import RequestContextMiddleware
from db import olap, oltp, mongo


logger = getLogger(__name__)

if settings.sentry_enabled:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    olap.olap_bd = olap.ClickHouseOlap(
        settings.clickhouse_host, settings.clickhouse_port
    )
    oltp.oltp_bd = oltp.KafkaOltp(
        f'{settings.kafka_host}:{settings.kafka_port}'
    )
    await oltp.oltp_bd.connect()
    await olap.olap_bd.connect()
    mongo.client = AsyncIOMotorClient(
        settings.mongodb_uri,
        uuidRepresentation='standard',
    )
    yield
    await oltp.oltp_bd.disconnect()
    mongo.client.close()


app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    docs_url='/ugc/api/v1/openapi',
    openapi_url='/ugc/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    logger.error("JWT error: %s", exc.message)
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


if settings.sentry_enabled:
    app.add_middleware(RequestContextMiddleware)

app.include_router(
    users_films.router,
    prefix='/ugc/api/v1/users_films',
    tags=['users_films']
)

app.include_router(
    ratings.router,
    prefix='/ugc/api/v1/ratings',
    tags=['ratings'],
)
app.include_router(
    reviews.router,
    prefix='/ugc/api/v1/reviews',
    tags=['reviews'],
)
app.include_router(
    bookmarks.router,
    prefix='/ugc/api/v1/bookmarks',
    tags=['bookmarks'],
)


if __name__ == '__main__':
    uvicorn.run(
        app=settings.uvicorn_app_name,
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        reload=True
    )
