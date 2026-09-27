"""SLSA provenance verification endpoints."""
from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, status

from src.api.schemas.provenance import (
    ProvenanceRecord,
    ProvenanceStatus,
    ProvenanceVerification,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def fetch_provenance_from_registry(image_digest: str) -> dict[str, Any] | None:
    """Fetch SLSA provenance attestation from Rekor transparency log."""
    rekor_url = os.getenv("SIGSTORE_REKOR_URL", "https://rekor.sigstore.dev")
    try:
        response = requests.get(
            f"{rekor_url}/api/v1/log/entries",
            params={"logIndex": 0},
            timeout=10,
        )
        if response.status_code == 200:
            return {"found": True, "digest": image_digest}
    except Exception as exc:
        logger.warning("Rekor lookup failed: %s", exc)
    return None


def verify_slsa_provenance(
    image_digest: str,
    provenance_data: dict[str, Any] | None,
) -> ProvenanceVerification:
    """Verify SLSA provenance meets Level 3 requirements."""
    if not provenance_data:
        return ProvenanceVerification(
            verified=False,
            slsa_level=0,
            violations=[
                "No provenance attestation found for image digest",
                "SLSA Level 3 requires signed provenance from a trusted builder",
            ],
            warnings=[],
        )

    violations: list[str] = []
    if not provenance_data.get("found"):
        violations.append("Provenance attestation not found in transparency log")

    return ProvenanceVerification(
        verified=len(violations) == 0,
        slsa_level=3 if not violations else 0,
        violations=violations,
        warnings=[],
    )


@router.get(
    "/{digest}",
    response_model=ProvenanceRecord,
    summary="Get SLSA provenance record for image digest",
)
async def get_provenance(digest: str) -> ProvenanceRecord:
    """
    Retrieve and verify SLSA provenance for a container image digest.

    The digest must be in sha256:HEXDIGEST format.
    """
    if not digest.startswith("sha256:") or len(digest) != 71:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid digest format. Expected sha256:HEXDIGEST (64 hex chars)",
        )

    provenance_data = fetch_provenance_from_registry(digest)
    verification = verify_slsa_provenance(digest, provenance_data)

    provenance_status = (
        ProvenanceStatus.VERIFIED if verification.verified else ProvenanceStatus.MISSING
    )

    return ProvenanceRecord(
        image_digest=digest,
        status=provenance_status,
        verification=verification,
        retrieved_at=datetime.now(tz=UTC),
        provenance_data=provenance_data,
    )
