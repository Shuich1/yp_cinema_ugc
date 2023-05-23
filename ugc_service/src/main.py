import logging

import uvicorn
from api.v1 import users_films
from core.config import settings
from core.logger import LOGGING
from db import olap, oltp
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
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


@app.on_event('startup')
async def startup():
    olap.olap_bd = olap.ClickHouseOlap(
        settings.CLICKHOUSE_HOST, settings.CLICKHOSE_PORT
    )
    oltp.oltp_bd = oltp.KafkaOltp(
        f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}'
    )
    await oltp.oltp_bd.connect()
    await olap.olap_bd.connect()


@app.on_event('shutdown')
async def shutdown():
    await oltp.oltp_bd.disconnect()

app.include_router(
    users_films.router,
    prefix='/ugc/api/v1/users_films',
    tags=['users_films']
)


if __name__ == '__main__':
    uvicorn.run(
        app=settings.UVICORN_APP_NAME,
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
