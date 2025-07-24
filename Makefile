# Makefile for mediator FastAPI project

.PHONY: run lint test build up down format makemigrations migrate downgrade history

# Run the FastAPI app locally (reload for dev)
run:
	uvicorn mediator.main:app --reload --host 0.0.0.0 --port 8000

# Build docker images
build:
	docker-compose build

# Start docker services
up:
	docker-compose up

# Stop docker services
down:
	docker-compose down

# Run Ruff linter and autofix
lint:
	ruff check mediator tests --fix

# Run tests using pytest
test:
	pytest tests

# Run pre-commit on all files
format:
	pre-commit run --all-files

# Create a new migration (requires message="...")
makemigrations:
	alembic revision --autogenerate -m "$(message)"

# Apply migrations
migrate:
	alembic upgrade head

# Downgrade to previous migration
downgrade:
	alembic downgrade -1

# Show migration history
history:
	alembic history --verbose
