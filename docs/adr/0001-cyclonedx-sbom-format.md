# ADR 0001: Use CycloneDX as SBOM Format

## Status

Accepted

## Context

We need to select a standard SBOM format for generating Software Bills of Materials for AI agent artifacts. The main candidates are:

- **CycloneDX**: OWASP-maintained, designed for security use cases, rich component support
- **SPDX**: Linux Foundation standard, widely adopted, strong license compliance focus

## Decision

We will use **CycloneDX 1.5** as our primary SBOM format.

## Rationale

1. **Security focus**: CycloneDX was designed specifically for security use cases including vulnerability management
2. **VEX support**: CycloneDX 1.4+ supports Vulnerability Exploitability eXchange (VEX)
3. **Python tooling**: `cyclonedx-python-lib` provides excellent Python SDK support
4. **OSV/NVD integration**: CycloneDX PURLs map directly to OSV/NVD vulnerability queries
5. **SLSA compatibility**: Works natively with SLSA provenance attestation workflows

## Consequences

- All SBOM generation uses CycloneDX 1.5 JSON format
- Storage format is `application/vnd.cyclonedx+json`
- PURL (Package URL) is required for all components to enable vulnerability correlation
