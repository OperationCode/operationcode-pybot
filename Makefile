.PHONY: help install lint lint-fix format test test-unit test-integration test-cov security ci docker-build docker-up docker-down clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies with poetry"
	@echo "  make lint             - Run ruff linter and formatter check"
	@echo "  make lint-fix         - Auto-fix linting and formatting issues"
	@echo "  make format           - Format code with ruff"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make security         - Run bandit and safety security scanners"
	@echo "  make ci               - Run all CI checks (lint, test-cov, security)"
	@echo "  make docker-build     - Build the Docker image"
	@echo "  make docker-up        - Start services with docker-compose"
	@echo "  make docker-down      - Stop services with docker-compose"
	@echo "  make clean            - Remove Python cache files and test artifacts"

# Install dependencies
install:
	poetry install

# Linting and formatting
lint:
	poetry run ruff check .
	poetry run ruff format --check .

lint-fix:
	poetry run ruff check --fix .
	poetry run ruff format .

format:
	poetry run ruff format .

# Testing
test:
	poetry run pytest

test-unit:
	poetry run pytest tests/unit/

test-integration:
	poetry run pytest tests/integration/

test-cov:
	SLACK_TOKEN=xoxb-test-token \
	SLACK_ADMIN_TOKEN=xoxb-admin-test-token \
	AIRTABLE_API_KEY=test-key \
	AIRTABLE_BASE_ID=test-base \
	poetry run pytest --cov=pybot --cov-report=xml --cov-report=term-missing -v --tb=short

# Security
security:
	poetry run bandit -r pybot -x pybot/_vendor --skip B101 -f txt

# CI - runs all checks that CI will run
ci: lint test-cov security
	@echo ""
	@echo "✓ All CI checks passed!"

# Docker
docker-build:
	docker build -f docker/Dockerfile -t pybot:latest .

docker-up:
	docker-compose -f docker/docker-compose.yml up

docker-down:
	docker-compose -f docker/docker-compose.yml down

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	rm -rf .ruff_cache htmlcov
	@echo "✓ Cleaned up Python cache files and test artifacts"
