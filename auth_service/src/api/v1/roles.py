from http import HTTPStatus
from logging import getLogger

from app import app
from core.init_extension import db
from flasgger.utils import swag_from
from flask import request
from marshmallow import ValidationError
from models.db import Role
from models.http import BaseResponse, RoleIdNameSchema, RoleSchema
from modules.tools import is_valid_json, is_valid_uuid, rbac_allow

logger = getLogger(__name__)


@app.route('/auth/api/v1/roles', methods=['GET', 'POST'])
@rbac_allow(['admin'], ['GET', 'POST'])
@is_valid_json(logger)
@swag_from('./docs/roles/roles_get.yml', methods=['GET'])
@swag_from('./docs/roles/roles_post.yml', methods=['POST'])
def roles_api():
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
        roles = Role.query.all()[offset:offset + limit]
        data = [
            {
                'id': role.id,
                'name': role.name,
            } for role in roles
        ]
        return data
    if request.method == 'POST':
        try:
            data = RoleSchema().load(request.json)
        except ValidationError as error:
            logger.warning(error.messages_dict)
            return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
        if Role.query.filter_by(name=data['name']).one_or_none() is not None:
            return BaseResponse().load({'msg': 'Role name exist'}), HTTPStatus.CONFLICT
        if 'id' in data and Role.query.filter_by(id=data['id']).one_or_none() is not None:
            return BaseResponse().load({'msg': 'UUID already used'}), HTTPStatus.CONFLICT
        role = Role(**{k: v for k, v in data.items() if k in ['name', 'id']})
        db.session.add(role)
        db.session.commit()
        logger.info('Role created %s / %s', str(role.id), str(role.name))
        return RoleIdNameSchema().load({'id': role.id, 'name': role.name})


@app.route('/auth/api/v1/roles/<role_id>', methods=['GET', 'PATCH', 'DELETE'])
@rbac_allow(['admin'], ['GET', 'PATCH', 'DELETE'])
@is_valid_json(logger)
@swag_from('./docs/roles/role_get.yml', methods=['GET'])
@swag_from('./docs/roles/role_patch.yml', methods=['PATCH'])
@swag_from('./docs/roles/role_delete.yml', methods=['DELETE'])
def role_api(role_id: int):
    err = list()
    if not is_valid_uuid(role_id):
        err.append('Bad role_id')
    else:
        role = Role.query.filter_by(id=role_id).one_or_none()
        if not role:
            err.append('Role_id is not exist')
    if len(err) > 0:
        logger.warning('\n'.join(err))
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
    if request.method == 'DELETE':
        db.session.delete(role)
        db.session.commit()
        return BaseResponse().load({'msg': 'Role deleted'}), HTTPStatus.OK
    if request.method == 'PATCH':
        if 'name' in request.json:
            role.name = request.json['name']
        db.session.commit()
    return RoleIdNameSchema().load({'id': role.id, 'name': role.name})
