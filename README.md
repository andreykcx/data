# Project Setup

This repository provides a minimal FastAPI backend and Vite/React frontend that can run together with Docker Compose or directly on your machine.

## Prerequisites
- Docker and Docker Compose v2
- Python 3.11+
- Node.js 18+ and npm

## Environment variables
Shared variables live in `.env` (and `.env.example` for reference):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- `DATABASE_URL` (used by the API)
- `API_BASE_URL` (used by the frontend to reach the API)
- `CORS_ORIGINS` (comma-separated origins the API will allow; defaults include `http://localhost:5173` and `http://frontend:5173`)
- `API_KEY` (optional; if set, upload endpoints require the `x-api-key` header)

Copy the example file when starting:
```bash
cp .env.example .env
```

When running the Docker Compose stack, the API is reachable at `http://api:8000`; local development can override the frontend target with `VITE_API_BASE_URL=http://localhost:8000`.

## Running with Docker
1. Build and start the stack:
   ```bash
   make up
   ```
   - API: http://localhost:8000 (reachable from other services at `http://api:8000`)
   - Frontend: http://localhost:5173
   - PostgreSQL: localhost:${POSTGRES_PORT:-5432}

2. Follow logs:
   ```bash
   make logs
   ```

3. Stop and clean up containers:
   ```bash
   make down
   ```

## Running locally without Docker
### Backend (FastAPI)
```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Vite/React)
```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev -- --host --port 5173
```

## Development commands
- Format code:
  ```bash
  make format
  ```
- Run tests:
  ```bash
  make test
  ```

## Production deployment
1. Clone the repository and prepare environment files:
   ```bash
   git clone <repo-url>
   cd data
   cp .env.example .env
   cp .env.frontend.example .env.frontend
   ```
   - `.env` supplies PostgreSQL and API variables (including `DATABASE_URL` and optional `API_KEY`).
   - `.env.frontend` sets the API base URL for the Vite build (defaults to `http://api:8000`).

2. Launch the production stack with the override file (multi-stage Dockerfiles build the API and frontend images):
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```
   - API: http://localhost:8000 (waits for Postgres health before starting; runs Alembic migrations on boot)
   - Frontend: http://localhost:8080

3. Validate the deployment:
   ```bash
   curl -f http://localhost:8000/health
   curl -X POST -F "file=@samples/xy_sample.csv" http://localhost:8000/datasets/upload
   ```
   If `API_KEY` is set, include `-H "x-api-key: $API_KEY"` in the upload request.

## Sample CSV for post-deploy checks
- Location: `samples/xy_sample.csv`
- Expected format: a header row `x,y` followed by numeric-only rows (integers or decimals) for both columns.
- Example contents:
  ```csv
  x,y
  1,1
  2,2
  3,2.5
  ```

You can reuse this file to confirm `/datasets/upload` works immediately after deployment.
