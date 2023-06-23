from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.requests import Request
from fastapi.security import HTTPBearer
from models import User
from pydantic import ValidationError
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from http import HTTPStatus


class JWTSchemaException(AuthJWTException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__(auto_error=False)

    async def __call__(self,
                       request: Request,
                       authorize: AuthJWT = Depends(),
                       ) -> User:
        await authorize.jwt_required()
        payload = await authorize.get_raw_jwt()
        return self._retrieve_user(payload)

    @staticmethod
    def _retrieve_user(jwt_payload: dict) -> User:
        try:
            return User(id=jwt_payload.get('sub'))
        except ValidationError:
            raise JWTSchemaException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                message='Invalid JWT schema',
            )
