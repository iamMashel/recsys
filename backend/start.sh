#!/bin/bash
set -e

# Render provides postgresql:// — convert to postgresql+asyncpg:// for SQLAlchemy
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
