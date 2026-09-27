"""Audit logging for all API gateway requests."""
from __future__ import annotations

import json
import logging
import time
from typing import Any

logger = logging.getLogger("audit")


def log_request(
    method: str,
    path: str,
    tenant_id: str,
    user_id: str,
    status_code: int,
    duration_ms: float,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log an API request to the structured audit log."""
    record: dict[str, Any] = {
        "event_type": "api_request",
        "method": method,
        "path": path,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        "timestamp": time.time(),
    }
    if extra:
        record.update(extra)

    logger.info(json.dumps(record))
