"""Unit tests for vulnerability scanning."""
from __future__ import annotations

import sys
import os

import pytest


def _setup_path():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../services/api"))


class TestVulnerabilityScanning:
    """Tests for vulnerability scanning logic."""

    def test_extract_cvss_score_v3(self):
        """CVSS V3 score is correctly extracted from severity array."""
        _setup_path()
        from src.api.routes.v1.dependencies import extract_cvss_score

        vuln = {
            "severity": [
                {"type": "CVSS_V3", "score": "9.8"},
                {"type": "CVSS_V2", "score": "7.0"},
            ]
        }
        score = extract_cvss_score(vuln)
        assert score == 9.8

    def test_extract_cvss_score_missing(self):
        """Missing severity returns 0.0."""
        _setup_path()
        from src.api.routes.v1.dependencies import extract_cvss_score

        vuln = {"severity": []}
        assert extract_cvss_score(vuln) == 0.0

    def test_extract_cvss_score_malformed(self):
        """Malformed severity entry returns 0.0 without raising."""
        _setup_path()
        from src.api.routes.v1.dependencies import extract_cvss_score

        vuln = {"severity": [{"type": "CVSS_V3", "score": "not-a-number"}]}
        assert extract_cvss_score(vuln) == 0.0

    def test_policy_deny_blocks_critical(self):
        """DENY decision includes all critical CVE IDs in blocking_ids."""
        _setup_path()
        from src.api.routes.v1.dependencies import assess_policy
        from src.api.schemas.vulnerability import VulnerabilityFinding

        findings = [
            VulnerabilityFinding(
                vuln_id="CVE-2024-0001",
                package_name="pkg-a",
                package_version="1.0.0",
                summary="Critical",
                cvss_score=9.1,
            ),
            VulnerabilityFinding(
                vuln_id="CVE-2024-0002",
                package_name="pkg-b",
                package_version="2.0.0",
                summary="Critical",
                cvss_score=9.9,
            ),
        ]
        decision = assess_policy(findings)
        assert decision.decision == "DENY"
        assert "CVE-2024-0001" in decision.blocking_ids
        assert "CVE-2024-0002" in decision.blocking_ids
        assert decision.critical_count == 2

    def test_osv_batch_returns_empty_on_no_queries(self):
        """Empty packages list returns empty results without calling API."""
        _setup_path()
        from src.api.routes.v1.dependencies import query_osv_batch

        result = query_osv_batch([])
        assert result == []
