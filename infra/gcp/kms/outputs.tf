output "keyring_id" {
  description = "KMS keyring ID"
  value       = google_kms_key_ring.supply_chain.id
}

output "sbom_key_id" {
  description = "KMS key ID for SBOM encryption"
  value       = google_kms_crypto_key.sbom_encryption.id
}

output "signing_key_id" {
  description = "KMS key ID for attestation signing"
  value       = google_kms_crypto_key.attestation_signing.id
}
