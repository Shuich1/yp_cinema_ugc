import json
from datetime import datetime, timezone
from http import HTTPStatus
from logging import getLogger

import pytz
from app import app
from core.init_extension import db, jwt_redis_blocklist
from flasgger.utils import swag_from
from flask import request
from flask_jwt_extended import (current_user, decode_token,
                                get_jwt, get_jwt_identity,
                                jwt_required)
from marshmallow import ValidationError
from models.db import User, UserLoginHistory, UserProfile, UserRefreshToken
from models.http import (AccessTokenScheme, AccessRefreshTokenScheme,
                         BaseResponse, LoginHistorySchema, LoginPasswordScheme,
                         ProfileSchema, UserScheme)
from modules.tools import is_valid_json
from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy import exc
from sqlalchemy.dialects.postgresql import insert

logger = getLogger(__name__)


@app.route('/auth/api/v1/cabinet/register', methods=['POST'])
@is_valid_json(logger)
@swag_from('./docs/cabinet/register.yml')
def cabinet_register():
    raw_data = json.loads(request.data.decode())
    try:
        data = LoginPasswordScheme().load(raw_data)
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST

    if User.query.filter_by(login=data['login']).first() is not None:
        return BaseResponse().load({'msg': 'The login is already exist'}), HTTPStatus.CONFLICT

    user = User(login=data['login'])
    user.set_password(password=data['password'])
    db.session.add(user)
    db.session.commit()

    return BaseResponse().load({'msg': 'User is registered'}), HTTPStatus.OK


@app.route('/auth/api/v1/cabinet/login', methods=['POST'])
@is_valid_json(logger)
@swag_from('./docs/cabinet/login.yml')
def cabinet_login():
    try:
        data = LoginPasswordScheme().load(request.json)
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
    user = User.query.filter_by(login=data['login']).one_or_none()
    if not user or not user.check_password(data['password']):
        logger.warning('Invalid username or password')
        return BaseResponse().load({'msg': 'Invalid username or password'}), HTTPStatus.NOT_FOUND

    return AccessRefreshTokenScheme().load(user.user_login()), HTTPStatus.OK


@app.route('/auth/api/v1/cabinet/refresh', methods=['POST'])
@jwt_required(refresh=True, verify_type=False)
@swag_from('./docs/cabinet/refresh.yml')
def cabinet_refresh():
    jwt = get_jwt()
    try:
        data = AccessTokenScheme().load(request.json)
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
    old_obj_user_refresh_token = current_user.check_refresh_token(
        access_token_jti=decode_token(data['access_token'], allow_expired=True)['jti'],
        refresh_token_jti=jwt['jti']
    )
    if not old_obj_user_refresh_token:
        return BaseResponse().load({'msg': 'Active refresh_token was not found'}), HTTPStatus.NOT_FOUND
    else:
        access_token = current_user.create_app_access_token()
        new_refresh_token = current_user.create_app_refresh_token(
            access_token_jti=jwt['jti'], old_refresh_token=old_obj_user_refresh_token
        )
        return AccessRefreshTokenScheme().load(
            {
                'access_token': access_token,
                'refresh_token': new_refresh_token,
            }
        ), HTTPStatus.OK


@app.route('/auth/api/v1/cabinet/logout', methods=['POST'])
@jwt_required()
@swag_from('./docs/cabinet/logout.yml')
def cabinet_logout():
    jwt = get_jwt()
    jwt_time = datetime.utcfromtimestamp(jwt['exp']).replace(tzinfo=pytz.UTC)
    remaining_time = jwt_time - datetime.now(timezone.utc)
    jwt_redis_blocklist.set(jwt['jti'], '', ex=remaining_time.seconds + 1,)

    user_refresh_token = UserRefreshToken.query.filter_by(access_token=jwt['jti']).one_or_none()
    if user_refresh_token is not None:
        db.session.delete(user_refresh_token)
        db.session.commit()

    return BaseResponse().load({'msg': 'User logout'}), HTTPStatus.OK


@app.route('/auth/api/v1/cabinet', methods=['GET'])
@is_valid_json(logger)
@jwt_required(optional=True)
@swag_from('./docs/cabinet/detail.yml')
def cabinet_detail():
    current_identity = get_jwt_identity()
    if current_identity:
        return UserScheme().load(
                {
                    'id': current_user.id,
                    'login': current_user.login,
                }
            ), HTTPStatus.OK
    else:
        return UserScheme().load(
                {
                    'id': '00000000-0000-0000-0000-000000000000',
                    'login': 'anonymous user',
                }
            ), HTTPStatus.OK


@app.route('/auth/api/v1/cabinet/edit', methods=['POST'])
@is_valid_json(logger)
@jwt_required()
@swag_from('./docs/cabinet/edit.yml')
def user_edit():
    user_id = get_jwt_identity()
    raw_data = json.loads(request.data.decode())
    try:
        data = ProfileSchema().load(raw_data)
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST

    insert_stmt = insert(UserProfile).values(
        user_id=user_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
    )
    do_update_stmt = insert_stmt.on_conflict_do_update(
        constraint='user_profile_user_id_key',
        set_=dict(first_name=data['first_name'],
                  last_name=data['last_name'],
                  email=data['email'],
                  )
    )

    try:
        db.session.execute(do_update_stmt)
        db.session.commit()
    except exc.IntegrityError as error:
        if error.orig.pgcode == UNIQUE_VIOLATION:
            if 'user_profile_email_key' in error.orig.pgerror:
                return BaseResponse().load({'msg': 'Email is already used'}), HTTPStatus.CONFLICT

    return BaseResponse().load({'msg': 'User updated'}), HTTPStatus.OK


@app.route('/auth/api/v1/cabinet/history', methods=['GET'])
@is_valid_json(logger)
@jwt_required()
@swag_from('./docs/cabinet/history.yml')
def user_history():
    # ограничем выдачу лимитом; хотим все записи, делаем через несколько запросов
    if 'limit' in request.args:
        limit = int(request.args.get('limit'))
        if limit > 100:
            limit = 100
    else:
        limit = 100

    if 'offset' in request.args:
        offset = int(request.args.get('offset'))
    else:
        offset = 0

    user_id = get_jwt_identity()
    history = UserLoginHistory.query.filter_by(user_id=user_id).all()[offset:offset+limit]

    result = list()
    for el in history:
        result.append(LoginHistorySchema().load(
            {
                'id': str(el.id),
                'user_agent': el.user_agent,
                'date': el.auth_date.isoformat(),
            }
            )
        )

    return result, HTTPStatus.OK
