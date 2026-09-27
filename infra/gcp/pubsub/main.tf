resource "google_pubsub_topic" "dead_letter" {
  project = var.project_id
  name    = "dead-letter-${var.environment}"
}

resource "google_pubsub_topic" "sbom_created" {
  project = var.project_id
  name    = "sbom-created-${var.environment}"

  message_retention_duration = "86400s"
}

resource "google_pubsub_topic" "provenance_failed" {
  project = var.project_id
  name    = "provenance-failed-${var.environment}"

  message_retention_duration = "86400s"
}

resource "google_pubsub_topic" "vulnerability_found" {
  project = var.project_id
  name    = "vulnerability-found-${var.environment}"

  message_retention_duration = "86400s"
}

resource "google_pubsub_subscription" "sbom_created_sub" {
  project = var.project_id
  name    = "sbom-created-sub-${var.environment}"
  topic   = google_pubsub_topic.sbom_created.name

  ack_deadline_seconds = 60

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }
}
