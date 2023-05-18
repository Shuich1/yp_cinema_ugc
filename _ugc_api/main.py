from fastapi import FastAPI

from api import common
from api.v1 import movies
from core.config import settings, configure_logging
from dependencies import producer

configure_logging(settings.log_config)
app = FastAPI(
    title='Movies UGC API',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
)


@app.on_event('startup')
async def startup():
    await producer.on_startup()


@app.on_event('shutdown')
async def shutdown():
    await producer.on_shutdown()


app.include_router(common.router, prefix='/api')
app.include_router(movies.router, prefix='/api/v1/movies')
