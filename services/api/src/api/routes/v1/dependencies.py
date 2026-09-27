"""Dependency vulnerability scanning endpoints."""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, status

from src.api.schemas.vulnerability import (
    DependencyScanRequest,
    DependencyScanResponse,
    PolicyDecision,
    VulnerabilityFinding,
)

logger = logging.getLogger(__name__)
router = APIRouter()

OSV_API_URL = "https://api.osv.dev/v1/querybatch"
CRITICAL_CVSS_THRESHOLD = 9.0
HIGH_CVSS_THRESHOLD = 7.0


def query_osv_batch(packages: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Query OSV API for vulnerability data on a batch of packages."""
    queries: list[dict[str, Any]] = []
    for pkg in packages:
        query: dict[str, Any] = {}
        if pkg.get("purl"):
            query["package"] = {"purl": pkg["purl"]}
        elif pkg.get("name") and pkg.get("ecosystem"):
            query["package"] = {"name": pkg["name"], "ecosystem": pkg["ecosystem"]}
        if pkg.get("version"):
            query["version"] = pkg["version"]
        if query:
            queries.append(query)

    if not queries:
        return []

    try:
        response = requests.post(
            OSV_API_URL,
            json={"queries": queries},
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException as exc:
        logger.warning("OSV API query failed: %s", exc)
        return []


def extract_cvss_score(vuln: dict[str, Any]) -> float:
    """Extract the highest CVSS score from a vulnerability record."""
    max_score = 0.0
    for severity in vuln.get("severity", []):
        if severity.get("type") == "CVSS_V3":
            try:
                score_str = str(severity.get("score", "0.0"))
                score = float(score_str.split("/")[-1]) if "/" in score_str else float(score_str)
                max_score = max(max_score, score)
            except (ValueError, IndexError):
                pass
    return max_score


def assess_policy(findings: list[VulnerabilityFinding]) -> PolicyDecision:
    """Apply vulnerability policy to findings and return allow/deny decision."""
    critical = [f for f in findings if f.cvss_score >= CRITICAL_CVSS_THRESHOLD]
    high = [f for f in findings if HIGH_CVSS_THRESHOLD <= f.cvss_score < CRITICAL_CVSS_THRESHOLD]

    if critical:
        return PolicyDecision(
            decision="DENY",
            reason=(
                f"Found {len(critical)} critical vulnerability(ies) "
                f"with CVSS >= {CRITICAL_CVSS_THRESHOLD}"
            ),
            critical_count=len(critical),
            high_count=len(high),
            total_count=len(findings),
            blocking_ids=[f.vuln_id for f in critical],
        )

    if high:
        return PolicyDecision(
            decision="WARN",
            reason=f"Found {len(high)} high severity vulnerability(ies) with CVSS >= {HIGH_CVSS_THRESHOLD}",
            critical_count=0,
            high_count=len(high),
            total_count=len(findings),
            blocking_ids=[],
        )

    return PolicyDecision(
        decision="ALLOW",
        reason="No critical or high vulnerabilities found",
        critical_count=0,
        high_count=0,
        total_count=len(findings),
        blocking_ids=[],
    )


@router.post(
    "/scan",
    response_model=DependencyScanResponse,
    summary="Scan dependency tree for vulnerabilities",
)
async def scan_dependencies(request: DependencyScanRequest) -> DependencyScanResponse:
    """
    Scan a dependency tree against OSV vulnerability feeds.

    Returns vulnerability findings and a policy decision (ALLOW/WARN/DENY).
    DENY is issued when any dependency has CVSS >= 9.0 (critical).
    """
    packages = [dep.model_dump() for dep in request.dependencies]
    osv_results = query_osv_batch(packages)

    findings: list[VulnerabilityFinding] = []
    for i, result in enumerate(osv_results):
        if i >= len(packages):
            break
        pkg = packages[i]
        for vuln in result.get("vulns", []):
            cvss_score = extract_cvss_score(vuln)
            findings.append(
                VulnerabilityFinding(
                    vuln_id=vuln.get("id", "UNKNOWN"),
                    package_name=pkg.get("name", "unknown"),
                    package_version=pkg.get("version", "unknown"),
                    summary=vuln.get("summary", ""),
                    severity=vuln.get("severity", []),
                    cvss_score=cvss_score,
                    fixed_versions=[
                        r.get("fixed", "")
                        for affected in vuln.get("affected", [])
                        for r in affected.get("ranges", [])
                        if r.get("fixed")
                    ],
                    references=[r.get("url", "") for r in vuln.get("references", [])[:5]],
                )
            )

    policy = assess_policy(findings)

    return DependencyScanResponse(
        scan_id=f"scan-{datetime.now(tz=UTC).strftime('%Y%m%d%H%M%S')}",
        scanned_at=datetime.now(tz=UTC),
        total_packages=len(packages),
        findings=findings,
        policy=policy,
    )
