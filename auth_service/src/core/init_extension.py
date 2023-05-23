from datetime import datetime, timedelta
from http import HTTPStatus
from logging import config as logging_config, getLogger
from uuid import uuid4

import redis
from core.config import settings
from core.logger import LOGGING
from flasgger import Swagger
from flask import Flask, request
from flask_jwt_extended import JWTManager, current_user, jwt_required
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from models.db import User, create_user_and_role_if_not_exist, db
from models.http import BaseResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)

logging_config.dictConfig(LOGGING)
logger = getLogger(__name__)

swagger = Swagger()
ma = Marshmallow()
jwt = JWTManager()


jwt_redis_blocklist = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
)

rate_limit_db = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=1
)


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'{settings.db_ms}://{settings.db_user}:{settings.db_pwd}@'\
        f'{settings.db_host}:{settings.db_port}/{settings.db_name}'
    db.init_app(app)
    app.app_context().push()
    migrate = Migrate(app, db)
    try:
        if settings.admin_login and settings.admin_password:
            create_user_and_role_if_not_exist(
                db, login=settings.admin_login, password=settings.admin_password, rolename='admin'
            )
    except BaseException as exception:
        logger.warning(exception.args)


def init_jwt(app: Flask):
    jwt.init_app(app)
    app.config["JWT_SECRET_KEY"] = settings.jwt_sectet_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=settings.jwt_access_token_expires)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=settings.jwt_refresh_token_expires)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()


def init_marshmallow(app: Flask):
    ma.init_app(app)


def init_swagger(app: Flask):
    app.config['SWAGGER'] = {
        'openapi': '3.0.2',
        'title': 'API для работы с сервисом авторизации',
        'version': '0.1.0',
        'components': {
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            },
        },
    }

    swagger.init_app(app)


def init_rate_limit(app: Flask):
    @app.before_request
    @jwt_required(optional=True, verify_type=False)
    def rate_limit_before_request():
        if current_user:
            user_id = current_user.id
        else:
            user_id = 'anonymous'

        pipe = rate_limit_db.pipeline()
        now = datetime.now()
        key = f'{user_id}:{now.minute}'
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = pipe.execute()
        request_number = result[0]
        if request_number > settings.request_limit:
            return BaseResponse().load({'msg': 'Too many requests'}), HTTPStatus.TOO_MANY_REQUESTS


def init_trace(app: Flask):
    resource = Resource(attributes={
        "service.name": app.name
    })
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_agent_host,
                agent_port=int(settings.jaeger_agent_port)
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    FlaskInstrumentor().instrument_app(app)

    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id and not settings.debug:
            return BaseResponse().load({'msg': 'Request-id is required'}), HTTPStatus.BAD_REQUEST
        else:
            request_id = uuid4()

    @app.after_request
    def after_request(response):
        request_id = request.headers.get('X-Request-Id')
        span = trace.get_current_span()
        span.set_attribute('http.request_id', request_id)
        return response
