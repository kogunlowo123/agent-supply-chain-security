"""Pydantic schemas for provenance endpoints."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProvenanceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    MISSING = "MISSING"
    INVALID = "INVALID"
    PENDING = "PENDING"


class ProvenanceVerification(BaseModel):
    verified: bool
    slsa_level: int = Field(..., ge=0, le=4)
    violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ProvenanceRecord(BaseModel):
    image_digest: str
    status: ProvenanceStatus
    verification: ProvenanceVerification
    retrieved_at: datetime
    provenance_data: dict[str, Any] | None = None
