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
- `CORS_ORIGINS` (comma-separated origins the API will allow)

Copy the example file when starting:
```bash
cp .env.example .env
```

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

## Production notes
- Build the frontend for production:
  ```bash
  cd frontend && npm install && npm run build
  ```
- You can serve the production build via `npm run preview` or swap the frontend service to an nginx/static image that serves the `dist/` directory.
