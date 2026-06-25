# Phase 2 Plan: Backend and Database Foundation

## Summary

Phase 2 makes the backend ready for real product modules without building Holdings/Watchlist CRUD yet.

The goal is to establish typed configuration, PostgreSQL connectivity, SQLAlchemy 2.x sync ORM structure, Alembic migrations, initial table models, core error handling, basic logging, and backend tests.

## In Scope

- Review existing backend structure.
- Refine `pydantic-settings` configuration.
- Add documented environment variables for database, CORS, and future LLM settings.
- Centralize SQLAlchemy engine, session, base model, and FastAPI database dependency.
- Configure Alembic to use the same settings and model metadata.
- Add initial SQLAlchemy models for v0 table shapes.
- Generate and apply the first Alembic migration.
- Add simple shared error handling and logging modules.
- Add or update backend tests for health/config/database behavior.
- Keep README and workflow docs updated.

## Out of Scope

- Holdings CRUD API routes.
- Watchlist CRUD API routes.
- Frontend Holdings or Watchlist pages.
- Market data provider integration.
- News provider integration.
- AI/LLM calls.
- Report generation.
- Chat.
- Authentication.
- Deployment automation.

## Implementation Plan

1. Backend structure review
   - Confirm `backend/pyproject.toml`, `uv.lock`, `app/main.py`, health module, tests, and Alembic files are understandable.
   - Keep the modular monolith convention under `backend/app/modules/`.

2. Core configuration
   - Refine `backend/app/core/config.py`.
   - Add typed settings for `DATABASE_URL`, `BACKEND_CORS_ORIGINS`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`.
   - Keep `.env.example` synchronized with supported settings.

3. Database connection
   - Refine `backend/app/core/database.py`.
   - Keep SQLAlchemy 2.x sync style.
   - Provide a reusable session dependency for future FastAPI routes.
   - Confirm connection to Docker PostgreSQL.

4. Alembic
   - Ensure Alembic reads `settings.database_url`.
   - Ensure Alembic can discover all model metadata.
   - Generate and apply the first migration.
   - Document upgrade, downgrade, and autogenerate commands.

5. Initial database models
   - Add simple table models only.
   - Include common fields such as `id`, `created_at`, and `updated_at` where useful.
   - Keep business logic out of models for now.

6. Error handling and logging
   - Add `backend/app/core/errors.py` for predictable API errors.
   - Add `backend/app/core/logging.py` for readable local logs.
   - Wire only minimal global handlers needed for Phase 2.

7. Tests and checks
   - Keep health endpoint test passing.
   - Add targeted tests for settings and database session behavior where practical.
   - Run `uv run pytest`.
   - Run `uv run ruff check .`.
   - Confirm GitHub Actions remains green.

## Initial Table Plan

Phase 2 should create tables that support later MVP features, but should not add CRUD routes yet.

Planned tables:

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

Recommended model fields:

- `holdings`: ticker, shares, average_cost, company_name, sector, notes, target_allocation, investment_thesis.
- `watchlist_items`: ticker, company_name, sector, reason_to_watch, notes.
- `reports`: report_type, title, content_markdown.
- `chat_sessions`: title.
- `chat_messages`: chat_session_id, role, content.
- `stock_notes`: ticker, note.
- `market_data_cache`: cache_key, provider, payload, fetched_at, expires_at.
- `settings`: key, value.

Use indexes for ticker fields, cache keys, settings keys, and foreign keys where useful.

## Acceptance Criteria

Phase 2 is complete when:

- Backend connects to PostgreSQL.
- SQLAlchemy 2.x sync ORM is configured.
- Alembic migrations work.
- Initial database tables can be created.
- Health check endpoint still works.
- Core error handling structure exists.
- Basic logging setup exists.
- Backend structure follows the modular monolith design.
- Backend tests pass.
- Backend lint passes.
- Database and migration workflow is documented.
- CI remains green.

Only after this should the project move to Phase 3: Holdings and Watchlist CRUD.
