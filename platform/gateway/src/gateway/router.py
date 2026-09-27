"""API Gateway router — routes requests to upstream services."""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class GatewayRouter:
    """Routes API requests to appropriate upstream services."""

    def __init__(self) -> None:
        self.routes: dict[str, str] = {
            "/api/v1/sbom": os.getenv("API_SERVICE_URL", "http://supply-chain-api:8000"),
            "/api/v1/provenance": os.getenv("API_SERVICE_URL", "http://supply-chain-api:8000"),
            "/api/v1/dependencies": os.getenv("API_SERVICE_URL", "http://supply-chain-api:8000"),
            "/api/v1/health": os.getenv("API_SERVICE_URL", "http://supply-chain-api:8000"),
        }

    def resolve_upstream(self, path: str) -> str | None:
        """Resolve the upstream URL for a given request path."""
        for prefix, upstream in self.routes.items():
            if path.startswith(prefix):
                return upstream
        return None

    async def forward(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Forward a request to the resolved upstream."""
        upstream = self.resolve_upstream(path)
        if not upstream:
            raise ValueError(f"No upstream configured for path: {path}")

        url = f"{upstream}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, **kwargs)
            return response
