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
                         BaseResponse, MailruUserSchema)
from modules.social_user import register_social_user

logger = getLogger(__name__)


def get_user_mailru() -> Optional[MailruUserSchema]:
    verification_code = request.args.get('code')
    if not verification_code:
        logger.warning('Verification code is not provided')
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST
    data = {
        'grant_type': 'authorization_code',
        'code': verification_code,
        'client_id': settings.mailru_client_id,
        'client_secret': settings.mailru_client_secret,
        'redirect_uri': f'{settings.base_uri}{request.path}'
    }
    response = requests.post('https://oauth.mail.ru/token', data)
    if not response.ok:
        logger.warning(response.content)
        return None
    try:
        tokens = BaseOAuthTokensSchema().load(response.json())
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return None
    response = requests.get(f"https://oauth.mail.ru/userinfo?access_token={tokens['access_token']}")
    if not response.ok:
        logger.warning(response.content)
        return None
    try:
        user_mailru = MailruUserSchema().load(response.json())
    except ValidationError as error:
        logger.warning(error.messages_dict)
        return None
    return user_mailru


@app.route('/api/oauth/mailru', methods=['GET'])
@swag_from('./docs/oauth.yml')
def oauth_mailru():
    user_mailru = get_user_mailru()
    if not user_mailru:
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.NOT_FOUND

    social_acc = SocialAccount.query.filter_by(social_id=user_mailru['id'], social_name='mailru').one_or_none()
    if not social_acc:
        result = register_social_user(
            social_name="mailru",
            social_id=user_mailru['id'],
            last_name=user_mailru['last_name'],
            first_name=user_mailru['first_name'],
            email=user_mailru['email']
        )
        if result[1] == HTTPStatus.OK:
            social_acc = result[2]
        else:
            return result

    return AccessRefreshTokenScheme().load(social_acc.user.user_login()), HTTPStatus.OK
