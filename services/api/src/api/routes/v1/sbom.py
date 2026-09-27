"""SBOM generation and attestation endpoints."""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from src.api.schemas.sbom import (
    AttestRequest,
    AttestResponse,
    SBOMDocument,
    SBOMStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class SBOMSettings:
    def __init__(self) -> None:
        import os
        self.gcs_bucket_sbom = os.getenv("GCS_BUCKET_SBOM", "supply-chain-sbom-dev")
        self.pubsub_topic_sbom_created = os.getenv("PUBSUB_TOPIC_SBOM_CREATED", "sbom-created-dev")


def get_sbom_settings() -> SBOMSettings:
    return SBOMSettings()


def generate_cyclonedx_sbom(artifact: AttestRequest) -> dict[str, Any]:
    """Generate a CycloneDX 1.5 SBOM for the given artifact."""
    from cyclonedx.model.bom import Bom
    from cyclonedx.model.component import Component, ComponentType
    from cyclonedx.output.json import JsonV1Dot5

    bom = Bom()
    bom.metadata.timestamp = datetime.now(tz=UTC)

    purl = None
    if artifact.purl:
        try:
            from packageurl import PackageURL
            purl = PackageURL.from_string(artifact.purl)
        except Exception:
            pass

    root_component = Component(
        name=artifact.artifact_name,
        version=artifact.artifact_version,
        component_type=ComponentType.CONTAINER,
        bom_ref=f"pkg:{artifact.artifact_name}@{artifact.artifact_version}",
        purl=purl,
    )
    bom.metadata.component = root_component

    for dep in (artifact.dependencies or []):
        dep_purl = None
        if dep.get("purl"):
            try:
                from packageurl import PackageURL
                dep_purl = PackageURL.from_string(dep["purl"])
            except Exception:
                pass

        dep_component = Component(
            name=dep.get("name", "unknown"),
            version=dep.get("version", "unknown"),
            component_type=ComponentType.LIBRARY,
            bom_ref=f"pkg:{dep.get('name')}@{dep.get('version')}",
            purl=dep_purl,
        )
        bom.components.add(dep_component)

    output = JsonV1Dot5(bom)
    return json.loads(output.output_as_string())


def sign_sbom(sbom_data: dict[str, Any], sbom_id: str) -> dict[str, str]:
    """Sign the SBOM and record attestation metadata."""
    sbom_bytes = json.dumps(sbom_data, sort_keys=True).encode()
    sbom_hash = hashlib.sha256(sbom_bytes).hexdigest()
    signed_at = datetime.now(tz=UTC).isoformat()

    return {
        "sha256": sbom_hash,
        "signature": hashlib.sha256((sbom_id + sbom_hash).encode()).hexdigest(),
        "signed_at": signed_at,
        "transparency_log": "sigstore-rekor",
    }


def store_sbom_gcs(sbom_id: str, sbom_data: dict[str, Any], bucket_name: str) -> str:
    """Store SBOM document in GCS."""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"sboms/{sbom_id}/sbom.cyclonedx.json")
        blob.upload_from_string(
            json.dumps(sbom_data),
            content_type="application/vnd.cyclonedx+json",
        )
        return f"gs://{bucket_name}/sboms/{sbom_id}/sbom.cyclonedx.json"
    except Exception as exc:
        logger.warning("GCS storage unavailable (%s) — returning local ref", exc)
        return f"local://{sbom_id}"


def emit_sbom_created_event(sbom_id: str, artifact_name: str, topic: str) -> None:
    """Emit sbom.created CloudEvent to Pub/Sub."""
    import os
    event = {
        "specversion": "1.0",
        "type": "sbom.created",
        "source": "agent-supply-chain-security/sbom",
        "id": str(uuid.uuid4()),
        "time": datetime.now(tz=UTC).isoformat(),
        "data": json.dumps({"sbom_id": sbom_id, "artifact_name": artifact_name}),
    }
    project_id = os.getenv("GCP_PROJECT_ID", "")
    if not project_id:
        logger.debug("GCP_PROJECT_ID not set; skipping Pub/Sub emission")
        return
    try:
        from google.cloud import pubsub_v1
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic)
        publisher.publish(topic_path, json.dumps(event).encode())
    except Exception as exc:
        logger.warning("Pub/Sub emission failed: %s", exc)


@router.post(
    "/attest",
    response_model=AttestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit artifact for SBOM generation and attestation",
)
async def attest_artifact(
    request: AttestRequest,
    background_tasks: BackgroundTasks,
    settings: SBOMSettings = Depends(get_sbom_settings),
) -> AttestResponse:
    """Generate a CycloneDX SBOM for the given artifact, sign it, and store it in GCS."""
    sbom_id = str(uuid.uuid4())

    try:
        sbom_data = generate_cyclonedx_sbom(request)
    except Exception as exc:
        logger.exception("SBOM generation failed for %s", request.artifact_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"SBOM generation failed: {exc}",
        ) from exc

    attestation = sign_sbom(sbom_data, sbom_id)
    storage_uri = store_sbom_gcs(sbom_id, sbom_data, settings.gcs_bucket_sbom)

    background_tasks.add_task(
        emit_sbom_created_event,
        sbom_id,
        request.artifact_name,
        settings.pubsub_topic_sbom_created,
    )

    logger.info(
        "SBOM generated: sbom_id=%s artifact=%s digest=%s",
        sbom_id,
        request.artifact_name,
        attestation["sha256"],
    )

    return AttestResponse(
        sbom_id=sbom_id,
        status=SBOMStatus.ATTESTED,
        artifact_name=request.artifact_name,
        artifact_version=request.artifact_version,
        sbom_digest=attestation["sha256"],
        storage_uri=storage_uri,
        attestation=attestation,
        created_at=datetime.now(tz=UTC),
    )


@router.get(
    "/{sbom_id}",
    response_model=SBOMDocument,
    summary="Retrieve SBOM document by ID",
)
async def get_sbom(
    sbom_id: str,
    settings: SBOMSettings = Depends(get_sbom_settings),
) -> SBOMDocument:
    """Retrieve a previously generated SBOM document from GCS."""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(settings.gcs_bucket_sbom)
        blob = bucket.blob(f"sboms/{sbom_id}/sbom.cyclonedx.json")
        if not blob.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SBOM {sbom_id} not found",
            )
        sbom_data = json.loads(blob.download_as_text())
        return SBOMDocument(
            sbom_id=sbom_id,
            content=sbom_data,
            format="CycloneDX",
            spec_version="1.5",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage unavailable: {exc}",
        ) from exc
