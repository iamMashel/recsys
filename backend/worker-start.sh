#!/bin/sh
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
exec celery -A workers.celery_app worker --loglevel=info --concurrency=2
