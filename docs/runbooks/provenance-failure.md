# Runbook: Provenance Verification Failure

## Symptoms

- `GET /api/v1/provenance/{digest}` returns `status: MISSING` or `status: INVALID`
- Deployment blocked with message "Provenance attestation missing or invalid"
- OPA policy denies deployment due to provenance violation

## Diagnosis

1. Check if the image was built from the main branch with the CI pipeline:
   ```bash
   git log --oneline -10
   gh run list --workflow=release.yml
   ```

2. Verify the image digest exists in the registry:
   ```bash
   gcloud artifacts docker images describe \
     us-central1-docker.pkg.dev/PROJECT/supply-chain/api@DIGEST
   ```

3. Check Rekor for the attestation:
   ```bash
   rekor-cli search --sha DIGEST
   ```

4. Verify cosign signature:
   ```bash
   cosign verify IMAGE_REF --certificate-oidc-issuer https://accounts.google.com
   ```

## Resolution

### Missing Provenance

If the image was built outside the CI pipeline:
1. Retrigger the CI pipeline for the same commit
2. The release workflow will sign the image and record provenance
3. Verify attestation appears in Rekor

### Invalid Provenance

If provenance exists but fails verification:
1. Check the signing identity used matches the expected service account
2. Verify the Rekor entry has not expired (default TTL: never for immutable log)
3. Escalate to the security team if tampering is suspected

## Emergency Override (Break Glass)

For production emergencies only, with dual approval:
```bash
./deploy/scripts/break_glass.sh --reason "REASON" --approver1 USER1 --approver2 USER2
```

All break-glass events are logged to the audit trail.
