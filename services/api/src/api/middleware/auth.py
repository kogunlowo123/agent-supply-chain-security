"""JWT authentication middleware."""
from __future__ import annotations

import logging
import os

import jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

UNPROTECTED_PATHS = {
    "/api/v1/health",
    "/api/v1/readiness",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Validate JWT Bearer tokens on protected routes."""

    def __init__(self, app, secret_key: str | None = None, algorithm: str = "HS256"):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "dev-secret-not-for-prod")
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in UNPROTECTED_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user_id = payload.get("sub", "")
            request.state.tenant_id = payload.get("tenant_id", "")
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Token expired"})
        except jwt.InvalidTokenError as exc:
            return JSONResponse(status_code=401, content={"detail": f"Invalid token: {exc}"})

        return await call_next(request)
