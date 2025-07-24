#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be available..."
until pg_isready -h db -p 5432 -U postgres > /dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL is available."

# Run Alembic migrations
echo "⏫ Running Alembic migrations..."
alembic upgrade head

# Start FastAPI app
echo "🚀 Starting FastAPI app..."
exec uvicorn mediator.main:app --host 0.0.0.0 --port 8000
