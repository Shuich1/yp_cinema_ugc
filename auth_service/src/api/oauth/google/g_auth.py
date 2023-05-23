import os
from http import HTTPStatus
from logging import getLogger
from typing import Dict, Optional

import google_auth_oauthlib
import googleapiclient.discovery
from app import app
from core.config import settings
from flasgger.utils import swag_from
from flask import request
from models.db import SocialAccount
from models.http import AccessRefreshTokenScheme, BaseResponse
from modules.social_user import register_social_user

logger = getLogger(__name__)

if settings.debug:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


client_secret_file = os.path.join(settings.base_dir, settings.rel_google_client_secret_file)
scopes = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def get_user_info() -> Optional[Dict]:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file=client_secret_file, scopes=scopes, state=request.args.get('state'))
    flow.redirect_uri = f'{settings.base_uri}{request.path}'

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    user_info_service = googleapiclient.discovery.build('oauth2', 'v2', credentials=flow.credentials)
    return user_info_service.userinfo().get().execute()


@app.route('/api/oauth/google', methods=['GET'])
@swag_from('./docs/oauth.yml')
def oauth_google_login():
    user_info = get_user_info()
    if user_info is None:
        return BaseResponse().load({'msg': 'Invalid body request'}), HTTPStatus.BAD_REQUEST

    social_acc = SocialAccount.query.filter_by(social_id=user_info['id'], social_name='google').one_or_none()
    if not social_acc:
        result = register_social_user(
            social_name="google",
            social_id=user_info['id'],
            last_name=user_info['family_name'],
            first_name=user_info['given_name'],
            email=user_info['email'],
        )
        if result[1] == HTTPStatus.OK:
            social_acc = result[2]
        else:
            return result

    return AccessRefreshTokenScheme().load(social_acc.user.user_login()), HTTPStatus.OK
