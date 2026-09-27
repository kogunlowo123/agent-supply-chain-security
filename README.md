# Agent Supply Chain Security

Enterprise AI security platform for AI agent supply chain security — SBOM generation, SLSA provenance, dependency vulnerability scanning, and artifact attestation for AI agent software.

## Overview

This platform provides end-to-end supply chain security for AI agents:

- **SBOM Generation**: CycloneDX-format Software Bill of Materials for AI agent artifacts
- **SLSA Provenance**: Level 3 provenance generation and verification for build artifacts
- **Vulnerability Scanning**: Real-time dependency scanning against OSV/NVD feeds
- **Artifact Attestation**: Sigstore/cosign-based signing and attestation
- **Policy Enforcement**: OPA-based policies blocking deployments with known vulnerabilities
- **LangGraph Agents**: Intelligent analysis agents for SBOM, provenance, and dependency auditing

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/sbom/attest` | Submit artifact for SBOM generation and attestation |
| GET | `/api/v1/provenance/{digest}` | Get SLSA provenance record |
| POST | `/api/v1/dependencies/scan` | Scan dependency tree for vulnerabilities |
| GET | `/api/v1/sbom/{id}` | Retrieve SBOM document |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/readiness` | Readiness check |

## Quick Start

```bash
make install
make docker-up
make test
```

## Technology Stack

- Python 3.12, FastAPI, uvicorn, pydantic v2
- LangGraph 0.2+, LiteLLM 1.40+ (Vertex AI/Gemini)
- sentence-transformers (BAAI/bge-large-en-v1.5)
- PostgreSQL + pgvector, OpenSearch, GCS
- Sigstore, OPA, Kyverno, Binary Authorization
- GCP: GKE, Cloud SQL, Pub/Sub, KMS, Artifact Registry

## License

Apache 2.0
