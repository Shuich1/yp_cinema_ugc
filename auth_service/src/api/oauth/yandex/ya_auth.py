from http import HTTPStatus
from logging import getLogger
from typing import Optional

import requests
from app import app
from core.config import settings
from flasgger.utils import swag_from
from flask import request
from marshmallow import ValidationError
from models.db import SocialAccount
from models.http import (AccessRefreshTokenScheme, BaseOAuthTokensSchema,
                         BaseResponse, YandexUserSchema)
from modules.social_user import register_social_user

logger = getLogger(__name__)


def get_user_yandex() -> Optional[YandexUserSchema]:
    verification_code = request.args.get('code')
    if not verification_code:
        logger.warning('Verification code is not provided')
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
    data = {
        'grant_type': 'authorization_code',
        'code': verification_code,
        'client_id': settings.yandex_client_id,
        'client_secret': settings.yandex_client_secret
    }
    response = requests.post('https://oauth.yandex.ru/token', data)
    if not response.ok:
        logger.warning(response.content)
        return None
    try:
        tokens = BaseOAuthTokensSchema().load(response.json())
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return None
    response = requests.get(
        'https://login.yandex.ru/info', headers={'Authorization': f"Oauth {tokens['access_token']}"}
    )
    if not response.ok:
        logger.warning(response.content)
        return None
    try:
        user_ya = YandexUserSchema().load(response.json())
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return None
    return user_ya


@app.route('/api/oauth/yandex', methods=['GET'])
@swag_from('./docs/oauth.yml')
def oauth_yandex_login():
    user_yandex = get_user_yandex()
    if not user_yandex:
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.NOT_FOUND

    social_acc = SocialAccount.query.filter_by(social_id=user_yandex['id'], social_name='yandex').one_or_none()
    if not social_acc:
        result = register_social_user(
            social_name="yandex",
            social_id=user_yandex['id'],
            last_name=user_yandex['last_name'],
            first_name=user_yandex['first_name'],
            email=user_yandex['default_email']
        )
        if result[1] == HTTPStatus.OK:
            social_acc = result[2]
        else:
            return result

    return AccessRefreshTokenScheme().load(social_acc.user.user_login()), HTTPStatus.OK
