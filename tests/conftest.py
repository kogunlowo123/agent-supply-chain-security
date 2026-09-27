"""Shared test fixtures and configuration."""
from __future__ import annotations

import os

import pytest


# Set test environment variables before any imports
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/supply_chain_security_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("GCS_BUCKET_SBOM", "test-sbom-bucket")
os.environ.setdefault("GCP_PROJECT_ID", "")
