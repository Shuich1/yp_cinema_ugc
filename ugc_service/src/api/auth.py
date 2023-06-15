from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.requests import Request
from fastapi.security import HTTPBearer
from models import User


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
        return User(id=jwt_payload.get('sub'))
