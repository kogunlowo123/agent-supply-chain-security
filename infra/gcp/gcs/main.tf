resource "google_storage_bucket" "audit_logs" {
  project       = var.project_id
  name          = "${var.project_id}-audit-logs-${var.environment}"
  location      = var.region
  force_destroy = false

  retention_policy {
    retention_period = 2592000
  }

  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "sbom_storage" {
  project       = var.project_id
  name          = "${var.project_id}-sbom-${var.environment}"
  location      = var.region
  force_destroy = var.environment != "prod"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 1825
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true

  encryption {
    default_kms_key_name = var.kms_key_id
  }

  logging {
    log_bucket        = google_storage_bucket.audit_logs.name
    log_object_prefix = "sbom-storage/"
  }
}
