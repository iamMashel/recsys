#!/bin/sh
# Render provides DATABASE_URL as postgresql:// — SQLAlchemy async needs postgresql+asyncpg://
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
