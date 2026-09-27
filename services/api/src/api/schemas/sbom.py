"""Pydantic schemas for SBOM endpoints."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SBOMStatus(str, Enum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    ATTESTED = "ATTESTED"
    FAILED = "FAILED"


class AttestRequest(BaseModel):
    artifact_name: str = Field(..., description="Name of the artifact to attest")
    artifact_version: str = Field(..., description="Version of the artifact")
    image_digest: str | None = Field(None, description="Container image digest (sha256:...)")
    purl: str | None = Field(None, description="Package URL for the artifact")
    dependencies: list[dict[str, Any]] | None = Field(
        default_factory=list,
        description="List of dependency descriptors",
    )
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class AttestResponse(BaseModel):
    sbom_id: str
    status: SBOMStatus
    artifact_name: str
    artifact_version: str
    sbom_digest: str = Field(..., description="SHA-256 digest of the SBOM document")
    storage_uri: str = Field(..., description="GCS URI of the stored SBOM")
    attestation: dict[str, str]
    created_at: datetime


class SBOMDocument(BaseModel):
    sbom_id: str
    content: dict[str, Any]
    format: str = "CycloneDX"
    spec_version: str = "1.5"
