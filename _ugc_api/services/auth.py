from http import HTTPStatus

import jwt
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer

from core.config import settings
from models import User


class JWTBearer(HTTPBearer):
    responses = {
        HTTPStatus.UNAUTHORIZED.value: {'description': 'Not authenticated'},
    }

    async def __call__(self, request: Request) -> User:
        auth = await super().__call__(request)
        token_payload = self.validate_token(auth.credentials)
        return self.get_user(token_payload)

    @staticmethod
    def validate_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                key=settings.jwt_secret,
                algorithms=settings.jwt_algorithm,
            )
        except jwt.exceptions.InvalidTokenError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid or expired token',
            )

    @staticmethod
    def get_user(token_payload: dict) -> User:
        try:
            return User(id=token_payload['sub'])
        except (KeyError, ValueError):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Invalid token schema',
            )
