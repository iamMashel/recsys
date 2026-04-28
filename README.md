# RecSys — Hybrid Movie Recommendation Platform

A production-grade, senior-level recommendation system that combines **collaborative filtering** (Gorse), **semantic similarity** (sentence-transformers + ChromaDB), and **popularity signals** into a hybrid ranking engine.

## Architecture

```
[ Nuxt 3 Frontend ]
        ↓
[ FastAPI (API Gateway) ]
        ↓
 ┌───────────────────────────────┐
 │  RecommenderService            │
 │  ├── Gorse (CF via REST)       │
 │  ├── ChromaDB (semantic)       │
 │  └── Hybrid ranking            │
 │      0.6·CF + 0.3·sem + 0.1·pop│
 └───────────────────────────────┘
        ↓
[ PostgreSQL ]   [ ChromaDB ]
        ↓
[ Celery Workers (Redis queue) ]
   ├── sync interactions → Gorse
   └── batch re-index embeddings
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Nuxt 3, TailwindCSS, Pinia |
| Backend | FastAPI, SQLAlchemy 2.0 async |
| Database | PostgreSQL 15 |
| CF Engine | Gorse |
| Semantic | sentence-transformers + ChromaDB |
| Queue | Celery + Redis |
| Infra | Docker Compose, NGINX |

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.12
- Node 20+

### 1. Clone & configure

```bash
git clone https://github.com/iamMashel/recsys.git
cd recsys

cp backend/.env.example backend/.env
# Edit backend/.env — set SECRET_KEY to a random 32-byte hex:
openssl rand -hex 32
```

### 2. Start all services

```bash
make up
# Brings up: postgres, redis, gorse, backend, celery-worker, celery-beat, frontend, nginx
```

### 3. Run migrations

```bash
make migrate
```

### 4. Seed MovieLens data

```bash
make seed
# Downloads ml-latest-small (~600k ratings, 9k movies) and loads it
```

### 5. Index embeddings + train fallback CF

```bash
make embed   # index all movie titles/genres into ChromaDB
make train   # build item-item CF model, cache in Redis
```

### 6. Sync to Gorse

```bash
# Trigger manually (or wait for Celery beat to run it hourly)
cd backend && python -c "from workers.tasks import sync_all_to_gorse; sync_all_to_gorse.delay()"
```

### 7. Open the app

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Gorse dashboard: http://localhost:8086

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register |
| `POST` | `/api/v1/auth/login` | Login (returns JWT) |
| `GET` | `/api/v1/auth/me` | Current user |
| `GET` | `/api/v1/items/` | List movies |
| `GET` | `/api/v1/items/{id}` | Movie detail |
| `POST` | `/api/v1/interactions/` | Record interaction |
| `GET` | `/api/v1/recommendations/me` | Your recommendations |

## Local Development (no Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit DB URL
make migrate
make dev              # http://localhost:8000

# Celery worker (separate terminal)
make worker

# Frontend
cd frontend
npm install
npm run dev           # http://localhost:3000
```

## Deployment

- **Backend** → Railway / Render (set `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY` env vars)
- **Frontend** → Vercel / Netlify (set `NUXT_PUBLIC_API_BASE` to backend URL)
