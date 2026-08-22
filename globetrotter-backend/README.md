# GlobeTrotter Backend

FastAPI backend service for GlobeTrotter built using vertical-slice architecture.

## Getting Started

### 1. Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose

### 2. Running Database Services

Start PostgreSQL and pgAdmin using Docker Compose:

```bash
docker compose up -d
```

### 3. Database Migrations

Run Alembic database migrations:

```bash
uv run alembic upgrade head
```

### 4. Running the Development API Server

Start the API server with auto-reload:

```bash
uv run uvicorn app.main:app --reload
```

The service will be accessible at `http://localhost:8000`. You can check the health endpoint at:
`http://localhost:8000/health`
