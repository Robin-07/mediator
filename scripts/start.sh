#!/bin/bash
set -e

echo "⏫ Running Alembic migrations..."
alembic upgrade head

echo "🚀 Starting FastAPI app..."
exec uvicorn mediator.main:app --host 0.0.0.0 --port 8000
