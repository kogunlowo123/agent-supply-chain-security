resource "google_service_account" "api_service" {
  project      = var.project_id
  account_id   = "supply-chain-api-${var.environment}"
  display_name = "Supply Chain Security API - ${var.environment}"
}

resource "google_service_account" "agent_runtime" {
  project      = var.project_id
  account_id   = "supply-chain-agents-${var.environment}"
  display_name = "Supply Chain Security Agents - ${var.environment}"
}

resource "google_project_iam_member" "api_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_project_iam_member" "api_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_project_iam_member" "api_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_project_iam_member" "api_secretmanager" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_service_account_iam_member" "api_workload_identity" {
  service_account_id = google_service_account.api_service.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[supply-chain/api]"
}

resource "google_project_iam_member" "agents_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_runtime.email}"
}

resource "google_service_account_iam_member" "agents_workload_identity" {
  service_account_id = google_service_account.agent_runtime.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[supply-chain/agent-runtime]"
}
