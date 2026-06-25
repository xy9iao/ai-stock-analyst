# Database Guide

This guide documents the Phase 2 database direction.

## Role of PostgreSQL

PostgreSQL stores application data for the local-first MVP.

The backend is the only layer that should connect to PostgreSQL. The frontend must use FastAPI routes instead of direct database access.

## SQLAlchemy Decision

The project uses SQLAlchemy 2.x sync ORM style for v0.

Reasons:

- simpler for a first full-stack project
- enough for the local-first MVP
- works cleanly with FastAPI service/repository structure
- can be changed later if async database access becomes necessary

## psycopg 3 Decision

The backend uses `psycopg` 3 as the PostgreSQL driver.

The expected SQLAlchemy URL format is:

```txt
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
```

## Alembic Migration Workflow

Alembic manages database schema changes.

A migration is a versioned change to the database. Migrations let the database schema evolve predictably as models change.

Common commands:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Phase 3 Note: No Schema Change

Phase 3 (Holdings/Watchlist CRUD) added **no migration**. The `holdings` and `watchlist_items` tables were created by the Phase 2 initial migration and were not altered — Phase 3 only added the API layers (`schemas` / `repository` / `service` / `router`) on top of the existing models. A new Alembic migration is only needed when a model's columns actually change.

## Phase 2 Initial Tables

Phase 2 should create initial table models and a first migration, but it should not add API CRUD behavior yet.

Initial tables:

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

## Recommended Fields

Common fields where useful:

- `id`
- `created_at`
- `updated_at`

`holdings`:

- `ticker`
- `shares`
- `average_cost`
- `company_name`
- `sector`
- `notes`
- `target_allocation`
- `investment_thesis`

`watchlist_items`:

- `ticker`
- `company_name`
- `sector`
- `reason_to_watch`
- `notes`

`reports`:

- `report_type`
- `title`
- `content_markdown`

`chat_sessions`:

- `title`

`chat_messages`:

- `chat_session_id`
- `role`
- `content`

`stock_notes`:

- `ticker`
- `note`

`market_data_cache`:

- `cache_key`
- `provider`
- `payload`
- `fetched_at`
- `expires_at`

`settings`:

- `key`
- `value`

## Index Guidance

Add indexes where they support obvious future access patterns:

- ticker lookups
- unique settings keys
- unique cache keys
- chat message session lookups

Avoid over-indexing before real query patterns exist.

## Phase 2 Acceptance

Database work is ready for Phase 3 when:

- the backend can connect to PostgreSQL
- SQLAlchemy models exist
- Alembic can autogenerate a migration
- Alembic can apply the migration
- backend tests and lint pass
- the database workflow is documented
