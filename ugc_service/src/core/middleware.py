from typing import Optional
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


REQUEST_ID_CTX_KEY = "request_id"

_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        request_id_val = request.headers.get('X-Request-Id')
        if not request_id_val:
            raise RuntimeError('Request id is required')
        request_id = _request_id_ctx_var.set(request_id_val)
        response = await call_next(request)
        # _request_id_ctx_var.reset(request_id)
        return response
