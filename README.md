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

### Option A — Render (recommended, one-click)

1. Fork this repo on GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your fork — Render reads `render.yaml` and provisions:
   - Web service (FastAPI backend)
   - Worker (Celery tasks)
   - Worker (Celery beat scheduler)
   - PostgreSQL database
   - Redis instance
4. After deploy, run the post-deploy steps in the Render Shell:
   ```bash
   alembic upgrade head
   python scripts/seed_data.py
   python -m recommender.train
   python -m recommender.embeddings
   ```
5. Set `ALLOWED_ORIGINS` to your Vercel frontend URL

### Option B — Railway

1. Install Railway CLI: `npm i -g @railway/cli && railway login`
2. ```bash
   railway init
   railway add --database postgresql
   railway add --database redis
   railway up
   ```
3. Set env vars in Railway dashboard (see `.env.example`)
4. For the Celery worker, create a second Railway service pointing to the same repo with start command:
   `celery -A workers.celery_app worker --loglevel=info`

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo
2. Set root directory to `frontend`
3. Add environment variable:
   ```
   NUXT_PUBLIC_API_BASE=https://your-backend.onrender.com
   ```
4. Deploy — Vercel auto-detects Nuxt 3

### Docker images (GitHub Container Registry)

Every push to `main` triggers `.github/workflows/publish.yml` which pushes:
- `ghcr.io/iamMashel/recsys-backend:latest`
- `ghcr.io/iamMashel/recsys-frontend:latest`

Use these images directly in Railway or any VPS.

### Required environment variables (production)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `SECRET_KEY` | 32-byte hex (`openssl rand -hex 32`) |
| `ALLOWED_ORIGINS` | Your Vercel URL (CORS) |
| `ENVIRONMENT` | `production` |
