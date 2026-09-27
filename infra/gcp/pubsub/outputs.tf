output "sbom_created_topic" {
  description = "Pub/Sub topic for SBOM created events"
  value       = google_pubsub_topic.sbom_created.name
}

output "provenance_failed_topic" {
  description = "Pub/Sub topic for provenance failures"
  value       = google_pubsub_topic.provenance_failed.name
}

output "vulnerability_found_topic" {
  description = "Pub/Sub topic for vulnerability findings"
  value       = google_pubsub_topic.vulnerability_found.name
}
