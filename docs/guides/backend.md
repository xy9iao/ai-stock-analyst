# Backend Guide

This guide documents the backend structure as implemented through Phase 3 (Holdings/Watchlist CRUD).

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
│   ├── main.py              # FastAPI app + router registration (health, holdings, watchlist, market, news, financials, reports)
│   ├── core/
│   │   ├── cache.py         # shared TTL cache (market data, news, financials)
│   │   ├── config.py        # typed pydantic-settings
│   │   ├── database.py      # engine, get_db session dependency, Base
│   │   ├── errors.py        # AppError + global handler
│   │   └── logging.py
│   ├── models/              # all SQLAlchemy models (one file per table)
│   └── modules/
│       ├── health/
│       │   └── router.py
│       ├── holdings/        # router → service → repository → schemas
│       │   ├── router.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── schemas.py
│       ├── watchlist/       # same layering as holdings
│       │   ├── router.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── schemas.py
│       ├── market_data/     # provider abstraction + cache-aside (Phase 4)
│       │   ├── provider.py        # MarketDataProvider Protocol
│       │   ├── providers/         # yfinance_provider.py
│       │   ├── service.py         # cache-aside (uses core/cache.py)
│       │   ├── router.py
│       │   └── schemas.py
│       ├── news/            # company news (Phase 5)
│       │   ├── provider.py        # NewsProvider Protocol
│       │   ├── providers/         # yfinance_news_provider.py
│       │   ├── service.py
│       │   ├── router.py
│       │   └── schemas.py
│       ├── financials/      # financial snapshots (Phase 5)
│       │   ├── provider.py        # FinancialDataProvider Protocol
│       │   ├── providers/         # yfinance_financials_provider.py
│       │   ├── service.py
│       │   ├── router.py
│       │   └── schemas.py
│       └── ai/              # AI report generation (Phase 6)
│           ├── llm_client.py       # the single OpenAI-compatible LLM call site
│           ├── context.py          # compact DB-context assembly
│           ├── prompt_builder.py   # system prompt (style + safety) + user prompt
│           ├── report_generator.py # orchestration
│           ├── repository.py       # reports table read/write
│           ├── router.py
│           └── schemas.py
├── alembic/
├── tests/                   # conftest.py (SQLite fixture) + test_*.py
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

## Modular Monolith Convention

The backend is a modular monolith.

Future business modules should live under `backend/app/modules/`.

Each feature module has four files (see `holdings/` and `watchlist/` for the reference implementation):

```txt
modules/<feature>/
├── router.py      # HTTP layer: routes, status codes, Depends(get_db)
├── service.py     # business logic: validation, not-found -> AppError(404)
├── repository.py  # the only layer that touches the DB Session
└── schemas.py     # Pydantic request/response models
```

SQLAlchemy models do **not** live in the module — all models are centralized in `backend/app/models/` (one file per table, re-exported in `models/__init__.py`). Modules call each other through normal Python imports and service functions, not internal network calls.

### Layered request flow

A write request flows straight down the layers and back:

`router` (parse + validate body via schema) → `service` (rules, ticker normalization, 404) → `repository` (SQLAlchemy `add`/`commit`/`refresh`) → ORM row → serialized through the `*Read` schema (`from_attributes=True`).

Boundary rules:

- Input validation lives in `schemas.py` (Pydantic) and fails fast with `422` — bad data never reaches the service or DB.
- "Not found" is a service decision: the repository returns `None`, the service raises `AppError(..., 404)`, and the global handler in `core/errors.py` formats the JSON.
- Partial updates use `PATCH` with `model_dump(exclude_unset=True)` so only the fields the client sent are changed.

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
