# Changelog

## [0.1.0] - 2024-01-15

### Added
- Initial implementation of agent supply chain security platform
- SBOM generation using CycloneDX format
- SLSA provenance generation and verification (Level 3 target)
- Dependency vulnerability scanning via OSV/NVD feeds
- Artifact signing and attestation using Sigstore
- OPA-based policy enforcement
- LangGraph agents: sbom-analyzer, provenance-verifier, dependency-auditor
- RAG over SLSA/CycloneDX/NIST SSDF documentation
- FastAPI REST API with OpenTelemetry instrumentation
- GCP infrastructure: GKE, Cloud SQL pgvector, GCS, Pub/Sub, KMS
- GitHub Actions CI/CD pipeline
- Helm charts for Kubernetes deployment
- ArgoCD application configuration
