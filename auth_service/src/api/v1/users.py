from http import HTTPStatus
from logging import getLogger

from app import app
from core.init_extension import db
from flasgger.utils import swag_from
from flask import request
from marshmallow import ValidationError
from models.db import Role, User
from models.http import BaseResponse, UserCreateScheme, UserRolesScheme
from modules.tools import is_valid_json, is_valid_uuid, rbac_allow
from sqlalchemy.exc import DataError

logger = getLogger(__name__)


@app.route('/auth/api/v1/users', methods=['GET', 'POST'])
@rbac_allow(['admin'], ['GET', 'POST'])
@is_valid_json(logger)
@swag_from('./docs/users/users_get.yml', methods=['GET'])
@swag_from('./docs/users/users_post.yml', methods=['POST'])
def users_api():
    if request.method == 'GET':
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
        users = User.query.all()[offset:offset + limit]
        return [
            UserRolesScheme().load(
                {'id': user.id, 'login': user.login, 'roles': [role.name for role in user.get_roles()]}
            ) for user in users
        ], HTTPStatus.OK
    if request.method == 'POST':
        try:
            data = UserCreateScheme().load(request.json)
        except ValidationError as error:
            logger.warning(error.messages_dict)
            return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
        if User.query.filter_by(login=data['login']).one_or_none() is not None:
            return BaseResponse().load({'msg': 'The login is already exist'}), HTTPStatus.CONFLICT
        if 'id' in data and User.query.filter_by(id=data['id']).one_or_none() is not None:
            return BaseResponse().load({'msg': 'UUID already used'}), HTTPStatus.CONFLICT
        user = User(**{k: v for k, v in data.items() if k in ['login', 'id']})
        user.set_password(password=data['password'])
        if 'roles' in request.json:
            try:
                roles = Role.query.filter(Role.name.in_(request.json['roles'])).all()
                if len(request.json['roles']) > len(roles):
                    raise ValueError
            except (DataError, ValueError):
                logger.warning('Wrong roles list: %s', request.json["roles"])
                return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
            else:
                user.set_roles(roles)
        db.session.add(user)
        db.session.commit()
    return UserRolesScheme().load({
            'id': user.id,
            'login': user.login,
            'roles': [role.name for role in user.get_roles()]
        }), HTTPStatus.OK


@app.route('/auth/api/v1/users/<user_id>', methods=['GET', 'PATCH', 'DELETE'])
@rbac_allow(['admin'], ['GET', 'PATCH', 'DELETE'])
@is_valid_json(logger)
@swag_from('./docs/users/user_get.yml', methods=['GET'])
@swag_from('./docs/users/user_patch.yml', methods=['PATCH'])
@swag_from('./docs/users/user_delete.yml', methods=['DELETE'])
def user_api(user_id: int):
    err = list()
    if not is_valid_uuid(user_id):
        err.append('Bad user_id')
    else:
        user = User.query.filter_by(id=user_id).one_or_none()
        if not user:
            err.append('User_id not exist')
    if len(err) > 0:
        logger.warning('\n'.join(err))
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return BaseResponse().load({'msg': 'User deleted'}), HTTPStatus.OK
    if request.method == 'PATCH':
        if 'login' in request.json:
            user.login = request.json['login']
        if 'roles' in request.json:
            try:
                roles = Role.query.filter(Role.name.in_(request.json['roles'])).all()
                if len(request.json['roles']) > len(roles):
                    raise ValueError
            except (DataError, ValueError):
                logger.warning('Wrong roles list: %s', request.json['roles'])
                return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
            else:
                user.set_roles(roles)
        db.session.commit()
    return UserRolesScheme().load({
            'id': user.id,
            'login': user.login,
            'roles': [role.name for role in user.get_roles()]
        }), HTTPStatus.OK
