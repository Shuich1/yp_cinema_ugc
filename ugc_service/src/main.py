import logging
from contextlib import asynccontextmanager
import uvicorn
from api.v1 import users_films
from core.config import settings
from core.logger import LOGGING
from db import olap, oltp
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from core.middleware import RequestContextMiddleware



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
    yield
    await oltp.oltp_bd.disconnect()


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
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


app.add_middleware(RequestContextMiddleware)

app.include_router(
    users_films.router,
    prefix='/ugc/api/v1/users_films',
    tags=['users_films']
)


if __name__ == '__main__':
    uvicorn.run(
        app=settings.uvicorn_app_name,
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
