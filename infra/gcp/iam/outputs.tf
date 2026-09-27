output "api_service_account_email" {
  description = "API service account email"
  value       = google_service_account.api_service.email
}

output "agent_runtime_service_account_email" {
  description = "Agent runtime service account email"
  value       = google_service_account.agent_runtime.email
}
