resource "google_kms_key_ring" "supply_chain" {
  project  = var.project_id
  name     = "supply-chain-keyring-${var.environment}"
  location = var.region
}

resource "google_kms_crypto_key" "sbom_encryption" {
  name     = "sbom-encryption-key"
  key_ring = google_kms_key_ring.supply_chain.id
  purpose  = "ENCRYPT_DECRYPT"

  rotation_period = "7776000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "attestation_signing" {
  name     = "attestation-signing-key"
  key_ring = google_kms_key_ring.supply_chain.id
  purpose  = "ASYMMETRIC_SIGN"

  version_template {
    algorithm = "EC_SIGN_P256_SHA256"
  }

  lifecycle {
    prevent_destroy = true
  }
}
