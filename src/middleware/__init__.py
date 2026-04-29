from configparser import ConfigParser
from fastapi import FastAPI
# https://github.com/encode/starlette/issues/420
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

REQUEST_CTX_KEY = "request_obj"

_request_ctx_var: ContextVar[str] = ContextVar(REQUEST_CTX_KEY, default=None)


def get_current_request():
    return _request_ctx_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):

        request_obj = _request_ctx_var.set(request)

        response = await call_next(request)

        _request_ctx_var.reset(request_obj)

        return response


def include_me(app: FastAPI, config: ConfigParser) -> None:
    app.add_middleware(RequestContextMiddleware)
