from http import HTTPStatus
from logging import getLogger
from typing import Dict, Optional

import requests
from app import app
from core.config import settings
from flasgger.utils import swag_from
from flask import request
from marshmallow import ValidationError
from models.db import SocialAccount
from models.http import AccessRefreshTokenScheme, BaseResponse, VKOAUTH2Scheme
from modules.social_user import register_social_user

logger = getLogger(__name__)


def get_user_info() -> Optional[Dict]:
    verification_code = request.args.get('code')
    if not verification_code:
        logger.warning('Verification code is not provided')
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST

    params = {
        'grant_type': 'authorization_code',
        'code': verification_code,
        'client_id': settings.vk_client_id,
        'client_secret': settings.vk_client_secret,
        'redirect_uri': f'{settings.base_uri}{request.path}'
    }
    response = requests.get('https://oauth.vk.com/access_token', params=params)

    try:
        data = VKOAUTH2Scheme().load(response.json())
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return None

    params = {
        'access_token': data['access_token'],
        'user_id': data['user_id'],
        'v': 5.131,
    }
    response = requests.get('https://api.vk.com/method/users.get', params=params)
    response_data = response.json()
    response_data['response'][0]['email'] = data['email']
    response_data['response'][0]['id'] = str(response_data['response'][0]['id'])

    return response_data['response'][0]


@app.route('/api/oauth/vk', methods=['GET'])
@swag_from('./docs/oauth.yml')
def oauth_vk():
    user_info = get_user_info()
    if user_info is None:
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST

    social_acc = SocialAccount.query.filter_by(social_id=user_info['id'], social_name='vk').one_or_none()
    if not social_acc:
        result = register_social_user(
            social_name="vk",
            social_id=str(user_info['id']),
            last_name=user_info['last_name'],
            first_name=user_info['first_name'],
            email=user_info['email'],
        )
        if result[1] == HTTPStatus.OK:
            social_acc = result[2]
        else:
            return result

    return AccessRefreshTokenScheme().load(social_acc.user.user_login()), HTTPStatus.OK
