# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

Please report security vulnerabilities to: security@example.com

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Measures

- All artifacts signed using Sigstore/cosign
- SLSA Level 3 provenance for all builds
- OPA policies enforce security gates
- Binary Authorization on GKE
- KMS-managed encryption keys
- Workload Identity on GKE
- Regular dependency scanning via OSV/NVD feeds
