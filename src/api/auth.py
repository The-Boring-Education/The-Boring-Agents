"""API authentication middleware for The Boring Agents."""

import logging
import secrets
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.config import Config

logger = logging.getLogger(__name__)


def _secrets_equal(provided: str, expected: str) -> bool:
    """Constant-time string comparison that tolerates unequal lengths."""
    if not provided or not expected:
        return False
    provided_bytes = provided.encode("utf-8")
    expected_bytes = expected.encode("utf-8")
    if len(provided_bytes) != len(expected_bytes):
        return False
    return secrets.compare_digest(provided_bytes, expected_bytes)


def extract_api_credential(request: Request) -> Optional[str]:
    """Extract inbound API credential from supported headers."""
    header_secret = request.headers.get("x-admin-secret")
    if header_secret:
        return header_secret.strip()

    api_key = request.headers.get("x-api-key")
    if api_key:
        return api_key.strip()

    authorization = request.headers.get("authorization")
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value.strip():
            return value.strip()

    return None


class APIAuthMiddleware(BaseHTTPMiddleware):
    """Require API credential on all non-public routes.

    Accepted headers:
    - x-admin-secret
    - x-api-key
    - Authorization: Bearer <secret>

    Credential is validated against AGENTS_API_KEY if set, otherwise ADMIN_SECRET.
    """

    PUBLIC_EXACT_PATHS = {
        "/api/v1",
        "/api/v1/health",
        "/api/v1/ping",
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    PUBLIC_PREFIXES = (
        "/docs/",
        "/redoc/",
    )

    def __init__(self, app: ASGIApp, config: Config):
        super().__init__(app)
        self.config = config

    def _is_public(self, path: str) -> bool:
        if path in self.PUBLIC_EXACT_PATHS:
            return True
        return any(path.startswith(prefix) for prefix in self.PUBLIC_PREFIXES)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        if self._is_public(path):
            return await call_next(request)

        expected = self.config.get_api_auth_secret()
        provided = extract_api_credential(request)

        if not _secrets_equal(provided or "", expected):
            logger.warning(
                "Unauthorized API request method=%s path=%s",
                request.method,
                path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
            )

        return await call_next(request)
