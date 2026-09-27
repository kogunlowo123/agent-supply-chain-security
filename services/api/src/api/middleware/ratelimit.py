"""Rate limiting middleware using slowapi."""
from __future__ import annotations

import os

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def get_limiter() -> Limiter:
    rpm = os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")
    return Limiter(
        key_func=get_remote_address,
        default_limits=[f"{rpm}/minute"],
    )


def setup_rate_limiter(app: FastAPI) -> None:
    limiter = get_limiter()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
