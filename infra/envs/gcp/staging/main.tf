terraform {
  required_version = ">= 1.8.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  backend "gcs" {
    bucket = "supply-chain-tfstate-staging"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "network" {
  source      = "../../../gcp/network"
  project_id  = var.project_id
  region      = var.region
  environment = "staging"
}

module "kms" {
  source      = "../../../gcp/kms"
  project_id  = var.project_id
  region      = var.region
  environment = "staging"
}

module "gcs" {
  source      = "../../../gcp/gcs"
  project_id  = var.project_id
  region      = var.region
  environment = "staging"
  kms_key_id  = module.kms.sbom_key_id
}

module "cloudsql" {
  source      = "../../../gcp/cloudsql-pg"
  project_id  = var.project_id
  region      = var.region
  environment = "staging"
  network_id  = module.network.network_id
}

module "gke" {
  source              = "../../../gcp/gke"
  project_id          = var.project_id
  region              = var.region
  environment         = "staging"
  network_id          = module.network.network_id
  subnet_id           = module.network.subnet_id
  pods_range_name     = module.network.pods_range_name
  services_range_name = module.network.services_range_name
}

module "pubsub" {
  source      = "../../../gcp/pubsub"
  project_id  = var.project_id
  environment = "staging"
}

module "iam" {
  source      = "../../../gcp/iam"
  project_id  = var.project_id
  environment = "staging"
}
