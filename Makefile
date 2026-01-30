.PHONY: help lint format test install run migrate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

lint: ## Run linter (ruff check)
	poetry run ruff check .

lint-fix: ## Run linter with auto-fix
	poetry run ruff check --fix .

format: ## Format code with ruff
	poetry run ruff format .

test: ## Run tests
	poetry run pytest tests/ -v

test-cov: ## Run tests with coverage report
	poetry run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	poetry run pytest-watch tests/

run: ## Run the application
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8080

migrate: ## Run database migrations
	poetry run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

check: lint ## Run all checks (lint + test)
	$(MAKE) test
