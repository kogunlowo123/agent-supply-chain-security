"""Integration tests for the SBOM API flow."""
from __future__ import annotations

import sys
import os

import pytest
from httpx import AsyncClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Create test client for the FastAPI app."""
    from src.api.main import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Tests for health and readiness endpoints."""

    @pytest.mark.anyio
    async def test_health_returns_200(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"

    @pytest.mark.anyio
    async def test_readiness_returns_200(self, client):
        response = await client.get("/api/v1/readiness")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestSBOMAttest:
    """Tests for SBOM attestation endpoint."""

    @pytest.mark.anyio
    async def test_attest_returns_202(self, client):
        """POST /sbom/attest returns 202 with sbom_id."""
        payload = {
            "artifact_name": "test-agent",
            "artifact_version": "1.0.0",
            "dependencies": [
                {"name": "langchain", "version": "0.1.0"},
            ],
        }
        response = await client.post("/api/v1/sbom/attest", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert "sbom_id" in data
        assert data["status"] == "ATTESTED"
        assert data["artifact_name"] == "test-agent"
        assert "sbom_digest" in data
        assert len(data["sbom_digest"]) == 64

    @pytest.mark.anyio
    async def test_attest_with_purl(self, client):
        """SBOM attestation with a valid PURL."""
        payload = {
            "artifact_name": "my-agent",
            "artifact_version": "2.0.0",
            "purl": "pkg:pypi/my-agent@2.0.0",
        }
        response = await client.post("/api/v1/sbom/attest", json=payload)
        assert response.status_code == 202

    @pytest.mark.anyio
    async def test_attest_missing_required_fields_returns_422(self, client):
        """Missing required fields return 422."""
        response = await client.post("/api/v1/sbom/attest", json={})
        assert response.status_code == 422


class TestDependencyScan:
    """Tests for dependency vulnerability scanning endpoint."""

    @pytest.mark.anyio
    async def test_scan_returns_200(self, client):
        """POST /dependencies/scan returns 200 with policy decision."""
        payload = {
            "dependencies": [
                {"name": "requests", "version": "2.31.0", "ecosystem": "PyPI"},
            ]
        }
        response = await client.post("/api/v1/dependencies/scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "findings" in data
        assert "policy" in data
        assert data["policy"]["decision"] in ("ALLOW", "WARN", "DENY")

    @pytest.mark.anyio
    async def test_scan_empty_dependencies_returns_422(self, client):
        """Empty dependencies list returns 422."""
        payload = {"dependencies": []}
        response = await client.post("/api/v1/dependencies/scan", json=payload)
        assert response.status_code == 422


class TestProvenanceEndpoint:
    """Tests for provenance endpoint."""

    @pytest.mark.anyio
    async def test_get_provenance_invalid_digest(self, client):
        """Invalid digest format returns 422."""
        response = await client.get("/api/v1/provenance/not-a-valid-digest")
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_get_provenance_valid_digest(self, client):
        """Valid sha256 digest returns provenance record."""
        digest = "sha256:" + "a" * 64
        response = await client.get(f"/api/v1/provenance/{digest}")
        assert response.status_code == 200
        data = response.json()
        assert data["image_digest"] == digest
        assert "status" in data
        assert "verification" in data
