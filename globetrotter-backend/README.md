# GlobeTrotter Backend ⚙️

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1+-009688?style=flat&logo=fastapi&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16--alpine-4169E1?style=flat&logo=postgresql&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F0E?style=flat&logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/Alembic-1.19+-6C757D?style=flat) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white) ![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white) ![uv](https://img.shields.io/badge/uv-Package_Manager-DE5E57?style=flat)

FastAPI backend service for **GlobeTrotter** built using a modular vertical-slice architecture.

For full project architecture, complete system prerequisites, and overall monorepo setup, refer to the [Top-Level Monorepo README](../README.md).

---

## ⚙️ Quickstart Guide

### 1. Prerequisites
- Python `>= 3.12`
- [uv](https://github.com/astral-sh/uv) package manager
- Docker & Docker Compose

### 2. Environment Setup
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Review and adjust variables in `.env` as needed (e.g. `DATABASE_URL`, `JWT_SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`).

### 3. Start Database Services
Launch PostgreSQL 16 Alpine and pgAdmin 4:

```bash
docker compose up -d
```

- **PostgreSQL**: `localhost:5432` (`globetrotter`/`globetrotter`)
- **pgAdmin**: `http://localhost:5050` (`admin@globetrotter.local`/`admin`)

### 4. Database Migrations
Run Alembic migrations to create tables (`users`, `cities`, `activities`, `trips`, `stops`, `trip_activities`, `stop_budget_overrides`, `trip_shares`):

```bash
uv run alembic upgrade head
```

### 5. Seed Reference Data
Seed reference cities and activities from CSV files (`seed_data/cities.csv` and `seed_data/activities.csv`):

```bash
uv run python -m app.scripts.seed_reference_data
```

*Note: The seed script is idempotent — existing records are updated and new records inserted.*

### 6. Start API Server
Launch the FastAPI server with auto-reload:

```bash
uv run uvicorn app.main:app --reload
```

- **API Base URL**: `http://localhost:8000`
- **Health Endpoint**: `http://localhost:8000/health`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

---

## 🧪 Running Backend Tests

Run all unit and API integration tests across feature slices:

```bash
uv run pytest
```
