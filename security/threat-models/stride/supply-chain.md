# STRIDE Threat Model: Agent Supply Chain Security

## System Overview

The Agent Supply Chain Security platform processes SBOM documents, verifies SLSA provenance, and scans dependency trees for vulnerabilities in AI agent software.

## STRIDE Analysis

### Spoofing

| Threat | Mitigation |
|--------|-----------|
| Attacker submits forged SBOM with clean dependency list | SBOM signatures verified via Sigstore/cosign before processing |
| Attacker impersonates trusted build system | SLSA Level 3 provenance with OIDC-bound signing prevents impersonation |
| JWT token theft enabling unauthorized API access | Short-lived tokens (1h), HTTPS-only, no cookie storage |

### Tampering

| Threat | Mitigation |
|--------|-----------|
| SBOM document modified after signing | SHA-256 digest stored and verified before analysis |
| Dependency tree manipulation to hide vulnerable packages | OSV API queried with exact package versions, not attestation data |
| Terraform state modification | GCS backend with versioning + IAM, state locked during apply |

### Repudiation

| Threat | Mitigation |
|--------|-----------|
| Attacker denies submitting malicious artifact | Immutable audit log in Cloud Logging, signed with KMS |
| Break-glass override without approval | Dual-approval required, logged to immutable audit trail |

### Information Disclosure

| Threat | Mitigation |
|--------|-----------|
| SBOM exposes internal architecture | SBOMs stored in GCS with IAM, not publicly accessible |
| Database credentials in logs | Structured logging with PII scrubbing processor in OTEL collector |
| Dependency vulnerability details exposed publicly | API requires authentication; rate limited |

### Denial of Service

| Threat | Mitigation |
|--------|-----------|
| Massive SBOM submission flood | Rate limiting (100 req/min per IP), async processing |
| OSV API exhaustion via scan requests | Request batching, cached results, circuit breaker |

### Elevation of Privilege

| Threat | Mitigation |
|--------|-----------|
| Agent escapes to host filesystem | Containers run as non-root with read-only filesystem |
| Kubernetes privilege escalation | Kyverno policy blocks privileged containers; PodSecurity enforced |
| GKE node compromise via metadata API | Workload Identity + metadata server access disabled |

## Risk Rating

Overall risk: **Medium** — Critical paths are protected by cryptographic attestation.
Residual risk: Supply chain attacks via compromised upstream dependencies.
