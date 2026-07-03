# Backend Guide

This guide documents the backend as implemented in **v0** (feature-complete, 2026-07-02).

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
│   ├── main.py              # FastAPI app + router registration (health, holdings, watchlist, market, news, financials, reports, chat)
│   ├── core/
│   │   ├── cache.py         # shared TTL cache (market data, news, financials)
│   │   ├── config.py        # typed pydantic-settings
│   │   ├── database.py      # engine, get_db session dependency, Base
│   │   ├── demo_session.py  # anonymous demo-session cookie middleware + TTL cleanup
│   │   ├── errors.py        # AppError + global handler
│   │   ├── llm_switch.py    # LLM master switch (settings-table row + TTL)
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
│       ├── ai/              # AI report generation (Phase 6)
│       │   ├── llm_client.py       # the single OpenAI-compatible LLM call site
│       │   ├── context.py          # compact DB-context assembly
│       │   ├── prompt_builder.py   # system prompt (style + safety) + user prompt
│       │   ├── report_generator.py # orchestration
│       │   ├── repository.py       # reports table read/write
│       │   ├── router.py
│       │   └── schemas.py
│       ├── chat/            # investment chat assistant (Phase 7)
│       │   ├── context.py          # toggleable context assembly (reuses ai/context)
│       │   ├── service.py          # orchestration + scope control + demo cap
│       │   ├── repository.py       # chat_sessions / chat_messages
│       │   ├── router.py
│       │   └── schemas.py
│       ├── session/         # demo-session reset endpoint (Phase 12)
│       │   └── router.py
│       └── admin/           # LLM master switch (token-gated) + /api/stats (Phase 12)
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

Use `pydantic-settings` for typed environment variables. `.env.example` documents expected variables, while local `.env` (repo root; `config.py` loads `../.env`) stores real local values and must not be committed.

Settings in use:

- `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `BACKEND_CORS_ORIGINS`
- `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (default `deepseek-v4-flash`) — consumed only by `modules/ai/llm_client.py`
- `MARKET_DATA_PROVIDER` (default `yfinance`) — selects the provider implementation

## Database

Database setup lives in `backend/app/core/database.py`: SQLAlchemy 2.x **sync** ORM style, with the shared declarative `Base`, engine creation from `settings.database_url`, the session factory, and the `get_db` FastAPI dependency that routes/repositories use. Tests override `get_db` with an in-memory SQLite session (see `tests/conftest.py`).

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

`backend/app/core/errors.py` defines `AppError(code, message, status_code)` plus a global handler. Services raise `AppError` for handled failures (e.g. not-found → 404, missing LLM key → 503); the handler formats the stable `{"detail": {"code", "message"}}` JSON body. No secrets or raw stack traces in normal responses.

## Logging

`backend/app/core/logging.py` provides a simple shared logging setup — readable local logs for startup, configuration, database, and API issues. Kept deliberately simple in v0.

## Demo hardening (Phase 12)

For the public demo (`DEMO_MODE=true`; off by default so local use is unchanged):

- **Anonymous session isolation** — `core/demo_session.py` middleware issues a `session_id`
  cookie; `holdings`, `watchlist_items`, `reports`, `chat_sessions` carry an indexed
  `session_id` column (`SessionScopedMixin`) and every repository filters by it. Local data
  lives in the permanent `"local"` bucket. Idle demo buckets are deleted after
  `DEMO_SESSION_TTL_DAYS` (lazy, throttled cleanup).
- **Cost defense (three layers):** ① DeepSeek prepaid balance = budget hard cap (operational);
  ② `core/llm_switch.py` — master switch stored in the `settings` table, default OFF, enabled
  via `POST /api/admin/llm` with a TTL, checked inside `llm_client` (the single gateway);
  ③ per-session caps in the `ai`/`chat` services, counted in **LLM calls** (agent-proof),
  derived from existing rows (no counter infra).
- **Observability** — `llm_client` writes one `llm_calls` row per call (tokens, latency,
  `route`/`steps` reserved for the agent version) + a structured log line; `GET /api/stats`
  aggregates them.

## Testing

`backend/tests/` holds the pytest suite (43 tests): `conftest.py` provides a `client` fixture backed by in-memory SQLite via a `get_db` override; market/news/financials providers and the LLM are monkeypatched at their factory/call seams, so tests run with **no network and no API cost**. `uv run pytest` also reports coverage (`pytest-cov`, measured — not gated).

## Health Endpoint

`GET /api/health` → `{ "status": "ok", "service": "ai-stock-analyst-backend" }` — used by Docker/dev to confirm the API is up.
