# Backend Guide

This guide documents the backend structure and Phase 2 direction.

## Purpose

The FastAPI backend owns:

- database access
- external API access
- AI/LLM integration
- report generation
- chat logic
- secrets and environment configuration

The frontend should call backend API routes. It should not directly call PostgreSQL, market data APIs, news APIs, or LLM APIs.

## Current Structure

```txt
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── modules/
│       └── health/
│           └── router.py
├── alembic/
├── tests/
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

## Modular Monolith Convention

The backend is a modular monolith.

Future business modules should live under `backend/app/modules/`.

Typical future module shape:

```txt
modules/example/
├── router.py
├── service.py
├── repository.py
├── models.py
└── schemas.py
```

Modules should call each other through normal Python imports and service functions, not internal network calls.

## Configuration

Backend configuration lives in `backend/app/core/config.py`.

Use `pydantic-settings` for typed environment variables. `.env.example` documents expected variables, while local `.env` stores real local values and must not be committed.

Phase 2 expected settings:

- `DATABASE_URL`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `BACKEND_CORS_ORIGINS`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

LLM settings are documented during Phase 2, but no AI calls should be implemented yet.

## Database

Database setup lives in `backend/app/core/database.py`.

Phase 2 should keep SQLAlchemy 2.x sync ORM style and provide:

- shared declarative base
- engine creation from `settings.database_url`
- session factory
- FastAPI session dependency for future routes

## Alembic

Alembic files live in `backend/alembic/` and `backend/alembic.ini`.

Alembic should read the same database URL as the app and use SQLAlchemy model metadata for autogeneration.

Common commands:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Error Handling

Phase 2 should add `backend/app/core/errors.py`.

The goal is a simple shared place for predictable application errors and API error responses. Avoid leaking secrets or raw internal stack traces in normal responses.

## Logging

Phase 2 should add `backend/app/core/logging.py`.

The goal is readable local logs for startup, configuration, database, and API issues. Keep logging simple in v0.

## Health Endpoint

Current endpoint:

```txt
GET /api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "ai-stock-analyst-backend"
}
```

The health endpoint should continue working throughout Phase 2.
