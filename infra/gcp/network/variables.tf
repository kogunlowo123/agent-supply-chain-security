variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "network_name" {
  description = "VPC network name"
  type        = string
  default     = "supply-chain-vpc"
}

variable "subnet_cidr" {
  description = "Subnet CIDR range"
  type        = string
  default     = "10.0.0.0/20"
}

variable "pods_cidr" {
  description = "GKE pods secondary CIDR"
  type        = string
  default     = "10.16.0.0/14"
}

variable "services_cidr" {
  description = "GKE services secondary CIDR"
  type        = string
  default     = "10.20.0.0/20"
}

variable "environment" {
  description = "Environment name"
  type        = string
}
