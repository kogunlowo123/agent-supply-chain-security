"""OpenTelemetry tracing middleware."""
from __future__ import annotations

import uuid

from fastapi import Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

tracer = trace.get_tracer("supply-chain-api")


class TracingMiddleware(BaseHTTPMiddleware):
    """Add trace context and request ID to each request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        with tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            attributes={
                "http.method": request.method,
                "http.url": str(request.url),
                "http.request_id": request_id,
            },
        ):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
