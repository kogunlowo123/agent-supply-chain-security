"""Unit tests for SBOM generation using CycloneDX."""
from __future__ import annotations

import json

import pytest


def make_attest_request(
    name: str = "my-agent",
    version: str = "1.0.0",
    purl: str | None = None,
    dependencies: list | None = None,
):
    """Build an AttestRequest-compatible dict."""
    from src.api.schemas.sbom import AttestRequest
    return AttestRequest(
        artifact_name=name,
        artifact_version=version,
        purl=purl,
        dependencies=dependencies or [],
    )


class TestSBOMGeneration:
    """Tests for CycloneDX SBOM generation."""

    def test_generates_valid_cyclonedx_sbom(self):
        """SBOM generation returns a valid CycloneDX 1.5 JSON document."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.sbom import generate_cyclonedx_sbom

        request = make_attest_request(
            name="test-agent",
            version="2.0.0",
        )
        sbom = generate_cyclonedx_sbom(request)

        assert isinstance(sbom, dict)
        assert sbom.get("bomFormat") == "CycloneDX"
        assert sbom.get("specVersion") in ("1.5", "1.6")
        assert "serialNumber" in sbom
        assert "metadata" in sbom

    def test_sbom_includes_root_component(self):
        """SBOM metadata contains the artifact as the root component."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.sbom import generate_cyclonedx_sbom

        request = make_attest_request(name="supply-chain-agent", version="1.2.3")
        sbom = generate_cyclonedx_sbom(request)

        metadata = sbom.get("metadata", {})
        component = metadata.get("component", {})
        assert component.get("name") == "supply-chain-agent"
        assert component.get("version") == "1.2.3"

    def test_sbom_includes_dependencies(self):
        """SBOM components list contains submitted dependencies."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.sbom import generate_cyclonedx_sbom

        request = make_attest_request(
            name="agent",
            version="1.0.0",
            dependencies=[
                {"name": "langchain", "version": "0.1.0"},
                {"name": "fastapi", "version": "0.110.0"},
            ],
        )
        sbom = generate_cyclonedx_sbom(request)

        components = sbom.get("components", [])
        component_names = {c.get("name") for c in components}
        assert "langchain" in component_names
        assert "fastapi" in component_names

    def test_sbom_sign_returns_sha256(self):
        """sign_sbom returns a sha256 hash and attestation metadata."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.sbom import sign_sbom

        sbom_data = {"bomFormat": "CycloneDX", "specVersion": "1.5"}
        sbom_id = "test-id-123"
        attestation = sign_sbom(sbom_data, sbom_id)

        assert "sha256" in attestation
        assert len(attestation["sha256"]) == 64
        assert "signed_at" in attestation
        assert attestation.get("transparency_log") == "sigstore-rekor"

    def test_vulnerability_policy_deny_on_critical(self):
        """Policy returns DENY when CVSS score >= 9.0."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.dependencies import assess_policy
        from src.api.schemas.vulnerability import VulnerabilityFinding

        findings = [
            VulnerabilityFinding(
                vuln_id="CVE-2024-9999",
                package_name="vulnerable-pkg",
                package_version="1.0.0",
                summary="Critical RCE vulnerability",
                cvss_score=9.8,
            )
        ]
        decision = assess_policy(findings)
        assert decision.decision == "DENY"
        assert decision.critical_count == 1
        assert "CVE-2024-9999" in decision.blocking_ids

    def test_vulnerability_policy_warn_on_high(self):
        """Policy returns WARN when CVSS score 7.0-8.9."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.dependencies import assess_policy
        from src.api.schemas.vulnerability import VulnerabilityFinding

        findings = [
            VulnerabilityFinding(
                vuln_id="CVE-2024-8888",
                package_name="risky-pkg",
                package_version="2.0.0",
                summary="High severity vulnerability",
                cvss_score=7.5,
            )
        ]
        decision = assess_policy(findings)
        assert decision.decision == "WARN"
        assert decision.high_count == 1

    def test_vulnerability_policy_allow_on_low(self):
        """Policy returns ALLOW when CVSS score < 7.0."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.dependencies import assess_policy
        from src.api.schemas.vulnerability import VulnerabilityFinding

        findings = [
            VulnerabilityFinding(
                vuln_id="CVE-2024-1111",
                package_name="low-risk-pkg",
                package_version="1.0.0",
                summary="Low severity",
                cvss_score=3.1,
            )
        ]
        decision = assess_policy(findings)
        assert decision.decision == "ALLOW"

    def test_vulnerability_policy_allow_no_findings(self):
        """Policy returns ALLOW when no vulnerabilities found."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))

        from src.api.routes.v1.dependencies import assess_policy

        decision = assess_policy([])
        assert decision.decision == "ALLOW"
        assert decision.total_count == 0
