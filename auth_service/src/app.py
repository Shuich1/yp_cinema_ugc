from core.config import settings
from core.init_extension import (init_db, init_jwt, init_marshmallow,
                                 init_rate_limit, init_swagger, init_trace)
from flask import Flask


def create_app():
    app = Flask(settings.app_name)
    app.secret_key = settings.app_secret_key
    init_swagger(app)
    init_marshmallow(app)
    init_db(app)
    init_jwt(app)
    if settings.enable_tracer:
        init_trace(app)
    init_rate_limit(app)

    return app


app = create_app()

from api.oauth.routes import *
from api.v1.routes import *

if __name__ == '__main__':
    app.run(host=settings.app_host, port=settings.app_port)
