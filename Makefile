.PHONY: help dev up down migrate seed test lint

help:
	@echo "Available commands:"
	@echo "  make dev      - Start backend dev server"
	@echo "  make up       - Start all services with Docker Compose"
	@echo "  make down     - Stop all services"
	@echo "  make migrate  - Run Alembic migrations"
	@echo "  make seed     - Seed database with MovieLens data"
	@echo "  make test     - Run backend tests"
	@echo "  make lint     - Run linting"

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

up:
	docker compose -f infra/docker-compose.yml up --build -d

down:
	docker compose -f infra/docker-compose.yml down

migrate:
	cd backend && alembic upgrade head

seed:
	python scripts/seed_data.py

test:
	cd backend && pytest tests/ -v

lint:
	cd backend && ruff check . && ruff format --check .
