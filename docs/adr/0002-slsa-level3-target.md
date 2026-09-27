# ADR 0002: Target SLSA Level 3 for Build Provenance

## Status

Accepted

## Context

We need to determine the appropriate SLSA (Supply chain Levels for Software Artifacts) provenance level to target for our build pipeline. SLSA levels range from 1 to 4, with increasing guarantees.

## Decision

We will target **SLSA Level 3** as our provenance standard.

## Rationale

1. **Meaningful security guarantees**: Level 3 provides non-falsifiable provenance via a hosted build platform
2. **Practical achievability**: GitHub Actions satisfies Level 3 requirements with SLSA GitHub Generator
3. **Industry standard**: Level 3 is the commonly accepted enterprise target
4. **Level 4 tradeoffs**: Level 4 requires hermetic builds which conflict with ML model downloads

## SLSA Level 3 Requirements Met

- Build defined in version-controlled configuration
- Provenance signed by build platform (GitHub Actions OIDC + Fulcio CA)
- Non-falsifiable attestation in Rekor transparency log
- Build environment is isolated (GitHub-hosted runners)

## Consequences

- All production images require valid SLSA Level 3 provenance attestation
- Deployments without provenance are blocked by OPA policy
- SLSA provenance is verified at admission time via Binary Authorization
