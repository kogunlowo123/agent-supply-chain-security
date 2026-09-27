output "sbom_bucket_name" {
  description = "SBOM storage bucket name"
  value       = google_storage_bucket.sbom_storage.name
}

output "sbom_bucket_url" {
  description = "SBOM storage bucket URL"
  value       = google_storage_bucket.sbom_storage.url
}
