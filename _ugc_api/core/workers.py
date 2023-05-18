from uvicorn.workers import UvicornWorker as BaseUvicornWorker

from .config import settings


class UvicornWorker(BaseUvicornWorker):
    CONFIG_KWARGS = {
        'loop': 'asyncio',
        'http': 'h11',
        'log_level': settings.log_level,
        'log_config': settings.log_config,
    }
