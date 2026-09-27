"""FastAPI application entry point for Agent Supply Chain Security API."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from src.api.middleware.ratelimit import setup_rate_limiter
from src.api.middleware.tenant import TenantMiddleware
from src.api.middleware.tracing import TracingMiddleware
from src.api.routes.v1 import dependencies, health, provenance, sbom

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_telemetry() -> None:
    """Configure OpenTelemetry tracing."""
    import os
    resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "supply-chain-api")})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    configure_telemetry()
    logger.info("Agent Supply Chain Security API starting up")
    yield
    logger.info("Agent Supply Chain Security API shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Agent Supply Chain Security API",
        description="Enterprise AI agent supply chain security platform",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://*.example.com"],
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Tenant-ID"],
    )
    app.add_middleware(TracingMiddleware)
    app.add_middleware(TenantMiddleware)

    setup_rate_limiter(app)

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(sbom.router, prefix="/api/v1/sbom", tags=["sbom"])
    app.include_router(provenance.router, prefix="/api/v1/provenance", tags=["provenance"])
    app.include_router(dependencies.router, prefix="/api/v1/dependencies", tags=["dependencies"])

    return app


app = create_app()
