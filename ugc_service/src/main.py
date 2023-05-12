import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from api.v1 import users_films

from core.config import settings
from core.logger import LOGGING
# from db import olap, oltp


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    # TODO
    # olap.olap_bd =
    # oltp.oltp_bd =
    pass


@app.on_event('shutdown')
async def shutdown():
    # TODO
    # await olap.olap_bd.disconnect()
    # await oltp.oltp_bd.disconnect()
    pass

app.include_router(users_films.router, prefix='/api/v1/users_films', tags=['users_films'])


if __name__ == '__main__':
    uvicorn.run(
        app=settings.UVICORN_APP_NAME,
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )