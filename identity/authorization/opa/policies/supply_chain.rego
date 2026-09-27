package supply_chain

import rego.v1

# Default deny deployment
default allow_deployment := false

# Allow deployment only when all checks pass
allow_deployment if {
    sbom_present
    provenance_valid
    not has_critical_vulnerability
}

# SBOM must be present for the image digest
sbom_present if {
    input.sbom_id != ""
    input.sbom_id != null
}

# Provenance attestation must exist and be verified
provenance_valid if {
    input.provenance.status == "VERIFIED"
    input.provenance.slsa_level >= 3
}

# No dependency with CVSS >= 9.0 (critical)
has_critical_vulnerability if {
    some finding in input.vulnerability_findings
    finding.cvss_score >= 9.0
}

# Policy decision with reasons
deployment_violations contains msg if {
    not sbom_present
    msg := "SBOM not present for image digest"
}

deployment_violations contains msg if {
    not provenance_valid
    msg := sprintf(
        "Provenance attestation missing or invalid (status=%s, slsa_level=%d)",
        [input.provenance.status, input.provenance.slsa_level],
    )
}

deployment_violations contains msg if {
    some finding in input.vulnerability_findings
    finding.cvss_score >= 9.0
    msg := sprintf(
        "Critical vulnerability %s (CVSS %.1f) in %s@%s blocks deployment",
        [finding.vuln_id, finding.cvss_score, finding.package_name, finding.package_version],
    )
}

# Warnings for high severity (7.0-8.9)
deployment_warnings contains msg if {
    some finding in input.vulnerability_findings
    finding.cvss_score >= 7.0
    finding.cvss_score < 9.0
    msg := sprintf(
        "High severity vulnerability %s (CVSS %.1f) in %s@%s — remediation recommended",
        [finding.vuln_id, finding.cvss_score, finding.package_name, finding.package_version],
    )
}

# Summary report
report := {
    "allow": allow_deployment,
    "violations": deployment_violations,
    "warnings": deployment_warnings,
}
