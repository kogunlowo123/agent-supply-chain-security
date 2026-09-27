.PHONY: install test lint format clean docker-up docker-down deploy-dev help

PYTHON := python3.12
UV := uv
PROJECT_NAME := agent-supply-chain-security
VERSION := $(shell cat VERSION)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd services/api && $(UV) pip install -e ".[dev]"
	cd services/rag-core && $(UV) pip install -e ".[dev]"
	cd services/agent-runtime && $(UV) pip install -e ".[dev]"
	pre-commit install

test: ## Run all tests
	pytest tests/ -v --tb=short -x

test-unit: ## Run unit tests only
	pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests
	pytest tests/integration/ -v --tb=short

test-security: ## Run security tests
	pytest tests/security/ -v --tb=short

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=services --cov-report=html --cov-report=term-missing --cov-fail-under=80

lint: ## Run linters
	ruff check services/ tests/
	mypy services/ --ignore-missing-imports

format: ## Format code
	ruff format services/ tests/

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage dist/ build/

docker-up: ## Start local development environment
	docker-compose up -d

docker-down: ## Stop local development environment
	docker-compose down

docker-build: ## Build Docker images
	docker-compose build

deploy-dev: ## Deploy to GCP dev environment
	cd infra/envs/gcp/dev && terraform init && terraform apply -auto-approve

run-api: ## Run API server locally
	cd services/api && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

evals: ## Run evaluation suite
	python evals/runners/ci_gate.py
