.PHONY: help run test fmt lint clean docker-build docker-run install

# Default target
help:
	@echo "Available commands:"
	@echo "  run          - Run the development server"
	@echo "  test         - Run tests"
	@echo "  fmt          - Format code with black"
	@echo "  lint         - Lint code with ruff"
	@echo "  typecheck    - Type check with mypy"
	@echo "  install      - Install dependencies"
	@echo "  clean        - Clean Python cache files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with docker-compose"
	@echo "  docker-down  - Stop docker-compose services"

# Development server
run:
	@echo "Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Run tests
test:
	@echo "Running tests..."
	pytest -v

# Format code
fmt:
	@echo "Formatting code..."
	black app/ tests/ alembic/
	ruff --fix app/ tests/ alembic/

# Lint code
lint:
	@echo "Linting code..."
	ruff app/ tests/ alembic/
	black --check app/ tests/ alembic/

# Type checking
typecheck:
	@echo "Type checking..."
	mypy app/ tests/

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -e .[dev]

# Clean Python cache
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	find . -type d -name ".mypy_cache" -delete

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker-compose build

docker-run:
	@echo "Starting services with docker-compose..."
	docker-compose up -d
	@echo "API: http://localhost:8080"
	@echo "Database: postgresql://aetheria:password@localhost:5432/aetheria_db"

docker-down:
	@echo "Stopping docker-compose services..."
	docker-compose down

docker-logs:
	@echo "Showing logs..."
	docker-compose logs -f api

# Development setup
setup-dev: install
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env with your configuration"
	@echo "Development setup complete!"

# Database operations
db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-downgrade:
	@echo "Downgrading database..."
	alembic downgrade -1

db-reset:
	@echo "Resetting database to base..."
	alembic downgrade base

db-revision:
	@echo "Creating new migration..."
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

db-current:
	@echo "Showing current migration..."
	alembic current

db-history:
	@echo "Showing migration history..."
	alembic history

# Check all (CI pipeline)
check-all: lint typecheck test
	@echo "All checks passed!"
