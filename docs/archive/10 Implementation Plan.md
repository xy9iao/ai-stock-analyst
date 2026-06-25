## 1. Purpose

This document tracks the implementation plan and current build progress for AI Stock Analyst.

The project has finished the first planning stage in Obsidian and has started implementation in the separate `ai-stock-analyst` repository.

The implementation should follow the planning documents and use a professional but manageable project structure.

---

# Current Progress

## Status Date

2026-06-21

## Current Phase

**Phase 3: Holdings and Watchlist CRUD**

## Progress Summary

- Phase 0 planning is complete.
- Phase 1 repository and development environment setup is complete.
- Phase 2 backend and database foundation is complete.
- The project is now ready to build manual Holdings and Watchlist CRUD.
- Phase 3 should focus on backend CRUD modules, schemas, tests, frontend pages, forms, tables, and frontend API calls.

## Current Build Priority

Do not start market data, AI reports, or chat yet.

First complete manual Holdings and Watchlist management:

1. Implement Holdings backend CRUD.
2. Implement Watchlist backend CRUD.
3. Add Pydantic request and response schemas.
4. Use repository/service/router structure.
5. Add backend CRUD tests.
6. Add frontend Holdings page.
7. Add frontend Watchlist page.
8. Add frontend API client functions.
9. Add basic forms and tables.
10. Keep documentation updated for beginner full-stack workflow.

---

# Phase 1: Repository and Development Environment Setup

## Status

Complete.

## Goal

Create the initial repository, frontend app, backend app, PostgreSQL database, and Docker Compose setup.

Phase 1 is complete when:

- The repository exists.
- The frontend can run.
- The backend can run.
- PostgreSQL can run.
- Docker Compose can start the local stack.
- The frontend can call a backend health check endpoint.

---

## Phase 1.1: Create Repository

### Tasks

- Create a new GitHub repository named `ai-stock-analyst`.
- Clone the repository locally.
- Add base folders.
- Add `.gitignore`.
- Add `.env.example`.
- Add a draft `README.md`.

### Initial Folder Structure

```txt
ai-stock-analyst/
├── .github/
│   └── workflows/
├── frontend/
├── backend/
├── docs/
│   └── development-workflow.md
├── prompts/
├── scripts/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

### Notes

The `docs/` folder in the repository should only contain implementation-facing documentation.

The broader planning documents remain in Obsidian.

---

## Phase 1.2: Initialize Backend

### Backend Stack

- Python
- uv
- FastAPI
- Uvicorn
- Pydantic v2
- pydantic-settings
- SQLAlchemy 2.x sync ORM
- Alembic
- psycopg 3 PostgreSQL driver
- pytest
- Ruff

### Backend Initial Structure

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
├── tests/
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

### Required Endpoint

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

### Success Criteria

- Backend starts locally.
- Health endpoint returns OK.
- Backend can be run inside Docker.

---

## Phase 1.3: Initialize Frontend

### Frontend Stack

- Next.js App Router
- React
- TypeScript
- pnpm
- Tailwind CSS
- shadcn/ui
- lucide-react

### Frontend Initial Structure

```txt
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── ui/
├── lib/
│   └── api/
│       └── client.ts
├── types/
├── package.json
├── next.config.ts
└── Dockerfile
```

### Required Behavior

The frontend should show:

- App title
- Basic Dashboard page
- Backend health check status

### Success Criteria

- Frontend starts locally.
- Frontend can call backend `/api/health`.
- Frontend can be run inside Docker.

---

## Phase 1.4: Add PostgreSQL

### Database

Use PostgreSQL as the local database.

### Docker Compose Service

PostgreSQL should run as a Docker service.

Required environment variables:

```txt
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

### Success Criteria

- PostgreSQL starts through Docker Compose.
- Backend can read database URL from environment variables.
- Backend is ready for later SQLAlchemy integration.

---

## Phase 1.5: Add Docker Compose

### Required Services

```txt
docker-compose
    ├── frontend
    ├── backend
    └── postgres
```

### Success Criteria

Running the following command should start the local development stack:

```bash
docker compose up --build
```

Expected result:

- Frontend runs on local port.
- Backend runs on local port.
- PostgreSQL runs on local port.
- Frontend can reach backend health endpoint.

---

## Phase 1.6: Add Basic README Draft

The README should include:

- Project name
- Short description
- Tech stack
- Local development setup
- Docker Compose command
- Environment variable setup
- Current project status

The README does not need to be polished yet.

A polished public README will be written after MVP completion.

---

# Phase 1 Acceptance Criteria

Phase 1 is complete when:

- [x] `ai-stock-analyst` repository exists.
- [x] `frontend/` exists and runs.
- [x] `backend/` exists and runs.
- [x] `postgres` runs through Docker Compose.
- [x] `docker compose up --build` works.
- [x] Backend health endpoint works.
- [x] Frontend displays backend health status.
- [x] `.env.example` documents required environment variables.
- [x] Initial README exists.
- [x] Beginner-friendly development workflow documentation exists.
- [x] Basic GitHub Actions CI workflow exists.

---

# Phase 2: Backend and Database Foundation

## Status

Complete.

## Goal

Build the backend foundation before implementing complex product features.

Phase 2 should make the backend ready for real modules such as Holdings, Watchlist, Reports, Chat, Market Data, News, and AI.

## Backend Stack Locked for Phase 2

- Python 3.12+
- `uv`
- FastAPI
- Uvicorn
- Pydantic v2
- `pydantic-settings`
- SQLAlchemy 2.x sync ORM
- Alembic
- PostgreSQL
- `psycopg` 3
- pytest
- Ruff

## Phase 2.1: Review Existing Backend Structure

### Tasks

- [x] Confirm `backend/` uses `uv`, `pyproject.toml`, and `uv.lock`.
- [x] Confirm FastAPI entrypoint is clear.
- [x] Confirm health module is separated from future business modules.
- [x] Confirm backend tests can run with `uv run pytest`.
- [x] Confirm linting can run with `uv run ruff check .`.

### Success Criteria

- Backend structure is understandable.
- Basic commands are documented.
- The project is ready for database wiring.

---

## Phase 2.2: Core Configuration

### Tasks

- [x] Create or refine `app/core/config.py`.
- [x] Use `pydantic-settings` for environment variables.
- [x] Load database URL from environment variables.
- [x] Keep secrets out of committed files.
- [x] Keep `.env.example` updated.

### Expected Settings

```txt
DATABASE_URL
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
BACKEND_CORS_ORIGINS
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

LLM settings can exist in `.env.example`, but Phase 2 does not need to implement AI calls yet.

### Success Criteria

- Backend configuration is typed.
- Missing or invalid configuration fails clearly.
- Local Docker Compose environment can provide required database settings.

---

## Phase 2.3: Database Connection

### Tasks

- [x] Create or refine `app/core/database.py`.
- [x] Configure SQLAlchemy engine using sync ORM style.
- [x] Configure session dependency for FastAPI routes and services.
- [x] Use `psycopg` 3 as the PostgreSQL driver.
- [x] Confirm backend can connect to Docker PostgreSQL.

### Success Criteria

- Backend can connect to PostgreSQL.
- Database session creation is centralized.
- Future modules can reuse the same database dependency.

---

## Phase 2.4: Alembic Setup

### Tasks

- [x] Initialize Alembic if not already done.
- [x] Configure Alembic to read the same database URL/settings.
- [x] Configure model metadata for autogeneration.
- [x] Create initial migration.
- [x] Document migration commands.

### Expected Commands

```bash
uv run alembic revision --autogenerate -m "create initial tables"
uv run alembic upgrade head
uv run alembic downgrade -1
```

### Success Criteria

- Alembic can generate migrations.
- Alembic can apply migrations to local PostgreSQL.
- Migration workflow is documented for the user.

---

## Phase 2.5: Initial Database Models

### Initial Tables

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

### Tasks

- [x] Create SQLAlchemy base model conventions.
- [x] Create initial SQLAlchemy models.
- [x] Add common fields where appropriate, such as `id`, `created_at`, and `updated_at`.
- [x] Keep models simple; do not implement full business logic yet.
- [x] Generate and apply migration for initial tables.

### Success Criteria

- Basic tables can be created in PostgreSQL.
- Models are ready for Phase 3 CRUD work.
- No Holdings or Watchlist API CRUD implementation is required yet.

---

## Phase 2.6: Core Error Handling and Logging

### Tasks

- [x] Create or refine `app/core/errors.py`.
- [x] Add a consistent API error response pattern.
- [x] Add basic exception handling for expected application errors.
- [x] Avoid leaking secrets or internal stack traces in normal API responses.
- [x] Create or refine `app/core/logging.py`.
- [x] Configure basic structured or readable application logging.
- [x] Ensure startup/database/config errors are easy to diagnose during local development.

### Success Criteria

- Backend has a clear place for shared error handling.
- Backend has a clear place for logging setup.
- Health/config/database failures are easier to debug.
- Error handling remains simple and does not over-engineer Phase 2.

---

## Phase 2.7: Backend Quality Checks

### Tasks

- [x] Add or update backend tests for health endpoint.
- [x] Add tests for error handling behavior if practical.
- [x] Add a lightweight database connectivity test if practical.
- [x] Run `uv run pytest`.
- [x] Run `uv run ruff check .`.
- [x] Run `uv run ruff format .` only if formatting changes are intended.
- [x] Ensure GitHub Actions still passes.

### Success Criteria

- Backend tests pass.
- Backend lint passes.
- CI remains green.

---

# Phase 2 Acceptance Criteria

Phase 2 is complete when:

- [x] Backend connects to PostgreSQL.
- [x] SQLAlchemy 2.x sync ORM is configured.
- [x] Alembic migrations work.
- [x] Initial database tables can be created.
- [x] Health check endpoint still works.
- [x] Core error handling structure exists.
- [x] Basic logging setup exists.
- [x] Backend structure follows modular monolith design.
- [x] Backend tests pass.
- [x] Backend lint passes.
- [x] Database and migration workflow is documented.

---

# Phase 3: Holdings and Watchlist CRUD

## Status

In progress.

## Goal

Build manual Holdings and Watchlist management before adding market data, AI reports, or chat.

Phase 3 should let the user create, view, update, and delete holdings and watchlist items through the backend API and frontend pages.

## Phase 3 Boundaries

Phase 3 includes:

- Holdings backend CRUD.
- Watchlist backend CRUD.
- Pydantic request and response schemas.
- Repository/service/router structure.
- Backend CRUD tests.
- Frontend Holdings page.
- Frontend Watchlist page.
- Frontend API client functions.
- Basic forms and tables.

Phase 3 does not include:

- Market data provider integration.
- Current price fetching.
- Real price charts.
- AI action labels.
- AI report generation.
- Chat.
- Import/export workflows.

Alembic already exists from Phase 2. Do not create a migration unless the existing holdings or watchlist schema needs to change.

## Phase 3.1: Confirm Existing Schema

### Tasks

- [ ] Inspect existing `holdings` and `watchlist_items` SQLAlchemy models.
- [ ] Confirm existing Alembic migration already creates the needed tables.
- [ ] Confirm model fields match MVP requirements.
- [ ] Decide whether a schema adjustment migration is needed.

### Holdings Fields

Required:

- `ticker`
- `shares`
- `average_cost`

Optional:

- `company_name`
- `sector`
- `notes`
- `target_allocation`
- `investment_thesis`

### Watchlist Fields

Required:

- `ticker`

Optional:

- `company_name`
- `sector`
- `reason_to_watch`
- `notes`

### Success Criteria

- Holdings and watchlist schemas are known.
- Any required schema change is documented before implementation.
- No unnecessary migration is created.

---

## Phase 3.2: Holdings Backend CRUD

### Tasks

- [ ] Create or refine Holdings module structure.
- [ ] Add Pydantic schemas for create, update, and response.
- [ ] Add repository functions for database operations.
- [ ] Add service functions for validation and business rules.
- [ ] Add FastAPI router endpoints.
- [ ] Register Holdings router in the main API.

### API Endpoints

Use these endpoints unless the existing backend convention already requires a different prefix:

```txt
GET    /api/holdings
POST   /api/holdings
GET    /api/holdings/{holding_id}
PATCH  /api/holdings/{holding_id}
DELETE /api/holdings/{holding_id}
```

### Validation

- `ticker` should be required, trimmed, and normalized to uppercase.
- `shares` should be greater than zero.
- `average_cost` should be greater than or equal to zero.
- Optional text fields may be empty or null.

### Success Criteria

- Holdings CRUD endpoints work.
- Invalid holdings input returns clear validation errors.
- Missing holding IDs return a clear not found response.

---

## Phase 3.3: Watchlist Backend CRUD

### Tasks

- [ ] Create or refine Watchlist module structure.
- [ ] Add Pydantic schemas for create, update, and response.
- [ ] Add repository functions for database operations.
- [ ] Add service functions for validation and business rules.
- [ ] Add FastAPI router endpoints.
- [ ] Register Watchlist router in the main API.

### API Endpoints

Use these endpoints unless the existing backend convention already requires a different prefix:

```txt
GET    /api/watchlist
POST   /api/watchlist
GET    /api/watchlist/{watchlist_item_id}
PATCH  /api/watchlist/{watchlist_item_id}
DELETE /api/watchlist/{watchlist_item_id}
```

### Validation

- `ticker` should be required, trimmed, and normalized to uppercase.
- Optional text fields may be empty or null.
- Watchlist items are not holdings and should not require shares or average cost.

### Success Criteria

- Watchlist CRUD endpoints work.
- Invalid watchlist input returns clear validation errors.
- Missing watchlist IDs return a clear not found response.

---

## Phase 3.4: Backend Tests

### Tasks

- [ ] Add Holdings API tests for list, create, read, update, delete.
- [ ] Add Watchlist API tests for list, create, read, update, delete.
- [ ] Add validation tests for invalid holdings input.
- [ ] Add validation tests for invalid watchlist input.
- [ ] Add not found tests.
- [ ] Confirm tests use isolated test data.
- [ ] Run `uv run pytest`.
- [ ] Run `uv run ruff check .`.

### Success Criteria

- Holdings backend tests pass.
- Watchlist backend tests pass.
- Existing Phase 1 and Phase 2 tests still pass.
- Backend lint still passes.

---

## Phase 3.5: Frontend API Client

### Tasks

- [ ] Add frontend API client functions for Holdings.
- [ ] Add frontend API client functions for Watchlist.
- [ ] Add TypeScript types matching backend response shapes.
- [ ] Use existing API client pattern from the health check.
- [ ] Keep API functions separate from page components.

### Success Criteria

- Frontend can call Holdings CRUD endpoints.
- Frontend can call Watchlist CRUD endpoints.
- API errors can be surfaced to UI components.

---

## Phase 3.6: Frontend Holdings Page

### Tasks

- [ ] Add Holdings page route.
- [ ] Display holdings in a basic table.
- [ ] Add create form.
- [ ] Add edit behavior.
- [ ] Add delete behavior.
- [ ] Add loading state.
- [ ] Add error state.
- [ ] Add empty state.

### UI Rules

- Use simple `shadcn/ui` table components first.
- Use React Hook Form and Zod if forms are already set up; otherwise keep forms simple and add them in the same pattern.
- Do not add market price, market value, unrealized P/L, or AI labels yet unless they are placeholder-free and backed by real data.

### Success Criteria

- User can manually add holdings from the UI.
- User can edit holdings from the UI.
- User can delete holdings from the UI.
- Data persists after refresh.

---

## Phase 3.7: Frontend Watchlist Page

### Tasks

- [ ] Add Watchlist page route.
- [ ] Display watchlist items in a basic table.
- [ ] Add create form.
- [ ] Add edit behavior.
- [ ] Add delete behavior.
- [ ] Add loading state.
- [ ] Add error state.
- [ ] Add empty state.

### UI Rules

- Watchlist items should not ask for shares or average cost.
- Do not display current price, charts, or AI labels yet.
- Keep the page focused on manual watchlist management.

### Success Criteria

- User can manually add watchlist items from the UI.
- User can edit watchlist items from the UI.
- User can delete watchlist items from the UI.
- Data persists after refresh.

---

## Phase 3.8: Documentation Updates

### Dev Repo Files To Update

```txt
README.md
AGENTS.md
docs/development-workflow.md
docs/backend.md
docs/database.md
docs/api.md
```

Create `docs/api.md` if it does not exist.

### Tasks

- [ ] Update current project status to Phase 3.
- [ ] Document Holdings CRUD endpoints.
- [ ] Document Watchlist CRUD endpoints.
- [ ] Document how to run backend tests.
- [ ] Document that market data, AI reports, and chat are out of scope for Phase 3.

### Success Criteria

- Future Codex sessions know Phase 3 scope.
- API docs are enough for frontend work.
- Docs do not imply market data or AI features are available.

---

# Phase 3 Acceptance Criteria

Phase 3 is complete when:

- [ ] User can manually add holdings.
- [ ] User can manually edit holdings.
- [ ] User can manually delete holdings.
- [ ] User can manually add watchlist items.
- [ ] User can manually edit watchlist items.
- [ ] User can manually delete watchlist items.
- [ ] Holdings data persists in PostgreSQL.
- [ ] Watchlist data persists in PostgreSQL.
- [ ] Backend Holdings CRUD tests pass.
- [ ] Backend Watchlist CRUD tests pass.
- [ ] Frontend displays holdings records.
- [ ] Frontend displays watchlist records.
- [ ] Frontend create/edit/delete flows work through the backend API.
- [ ] Existing health check still works.
- [ ] CI remains green.
- [ ] Phase 3 does not include market data, AI reports, or chat.
