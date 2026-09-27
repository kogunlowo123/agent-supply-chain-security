"""Health and readiness check endpoints."""
from __future__ import annotations

import time
from functools import lru_cache

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

router = APIRouter()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/supply_chain_security"
    otel_service_name: str = "agent-supply-chain-security"
    otel_exporter_otlp_endpoint: str = ""
    service_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: float


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return service health status."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.app_env,
        timestamp=time.time(),
    )


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness_check(settings: Settings = Depends(get_settings)) -> ReadinessResponse:
    """Return service readiness status with dependency checks."""
    checks: dict[str, str] = {}

    try:
        import psycopg2
        conn = psycopg2.connect(settings.database_url, connect_timeout=3)
        conn.close()
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {type(exc).__name__}"

    all_ok = all(v == "ok" for v in checks.values())
    return ReadinessResponse(
        status="ready" if all_ok else "not_ready",
        checks=checks,
    )
