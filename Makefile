.PHONY: help dev up down migrate seed test lint worker beat embed train

help:
	@echo "Available commands:"
	@echo "  make dev      - Start backend dev server"
	@echo "  make worker   - Start Celery worker"
	@echo "  make beat     - Start Celery beat scheduler"
	@echo "  make up       - Start all services with Docker Compose"
	@echo "  make down     - Stop all services"
	@echo "  make migrate  - Run Alembic migrations"
	@echo "  make seed     - Seed database with MovieLens data"
	@echo "  make embed    - Index item embeddings into ChromaDB"
	@echo "  make train    - Build CF model and cache in Redis"
	@echo "  make test     - Run backend tests"
	@echo "  make lint     - Run linting"

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd backend && celery -A workers.celery_app worker --loglevel=info

beat:
	cd backend && celery -A workers.celery_app beat --loglevel=info

up:
	docker compose -f infra/docker-compose.yml up --build -d

down:
	docker compose -f infra/docker-compose.yml down

migrate:
	cd backend && alembic upgrade head

seed:
	python scripts/seed_data.py

embed:
	cd backend && python -m recommender.embeddings

train:
	cd backend && python -m recommender.train

test:
	cd backend && pytest tests/ -v

lint:
	cd backend && ruff check . && ruff format --check .
