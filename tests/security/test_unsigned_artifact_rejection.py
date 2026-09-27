"""Security tests for unsigned artifact rejection policies."""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))


class TestUnsignedArtifactRejection:
    """Tests verifying that unsigned/unattested artifacts are rejected."""

    def test_missing_provenance_reported_as_violation(self):
        """Missing provenance triggers a SLSA level 0 result with violations."""
        from src.api.routes.v1.provenance import verify_slsa_provenance

        result = verify_slsa_provenance("sha256:" + "0" * 64, None)

        assert result.verified is False
        assert result.slsa_level == 0
        assert any("provenance" in v.lower() for v in result.violations)

    def test_sbom_digest_is_deterministic(self):
        """Same SBOM content always produces the same SHA-256 digest."""
        import json
        import hashlib
        from src.api.routes.v1.sbom import sign_sbom

        sbom_data = {"bomFormat": "CycloneDX", "specVersion": "1.5", "components": []}
        att1 = sign_sbom(sbom_data, "test-id-abc")
        att2 = sign_sbom(sbom_data, "test-id-abc")

        assert att1["sha256"] == att2["sha256"]

    def test_critical_vulnerability_results_in_deny(self):
        """Critical CVE (CVSS >= 9.0) results in DENY policy decision."""
        from src.api.routes.v1.dependencies import assess_policy
        from src.api.schemas.vulnerability import VulnerabilityFinding

        findings = [
            VulnerabilityFinding(
                vuln_id="CVE-2024-CRITICAL",
                package_name="exploit-pkg",
                package_version="0.0.1",
                summary="Remote code execution",
                cvss_score=10.0,
            )
        ]
        decision = assess_policy(findings)
        assert decision.decision == "DENY"

    def test_no_vulnerabilities_results_in_allow(self):
        """Clean dependency scan results in ALLOW policy decision."""
        from src.api.routes.v1.dependencies import assess_policy

        decision = assess_policy([])
        assert decision.decision == "ALLOW"
        assert len(decision.blocking_ids) == 0
