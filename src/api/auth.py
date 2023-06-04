from http import HTTPStatus

import jwt
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.security import HTTPBearer

from core.config import settings
from models import User


class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> None:
        auth_scheme = await super().__call__(request)
        if not auth_scheme:
            raise HTTPException(
                HTTPStatus.UNAUTHORIZED,
                'Authorization header is missing or invalid',
            )

        token = auth_scheme.credentials
        payload = self._decode_token(token)

        return self._retrieve_user(payload)

    @staticmethod
    def _decode_token(token: str) -> str:
        try:
            return jwt.decode(token, settings.jwt_secret_key, algorithms='HS256')
        except jwt.exceptions.InvalidTokenError as ex:
            raise HTTPException(HTTPStatus.UNAUTHORIZED, ex.args[0])

    @staticmethod
    def _retrieve_user(jwt_payload: dict) -> User:
        return User(id=jwt_payload.get('sub'))
