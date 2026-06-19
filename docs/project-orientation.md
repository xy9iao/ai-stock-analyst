# AI Stock Analyst v0 MVP Orientation - Phase 2 Handoff

Use this document as the single handoff prompt/context for the `ai-stock-analyst` implementation repo.

This file merges the original v0 orientation with the current Phase 2 progress from `10 Implementation Plan.md`.

Current status:

- Phase 0 planning is complete.
- Phase 1 repository and development environment setup is complete.
- Current active phase: **Phase 2: Backend and Database Foundation**.
- Do not start Holdings/Watchlist CRUD yet.

Status date: 2026-06-19

---

## 1. Product Summary

AI Stock Analyst is a local-first AI-powered stock research assistant.

The product helps a beginner investor understand:

- What happened in the market.
- Why major indexes or stocks moved.
- What news matters.
- How current holdings are doing.
- Which watchlist stocks need attention.
- Whether an action such as hold, add gradually, wait, reduce, sell, or research further may be reasonable.

The application is for investment research and decision support only.

It is not:

- An automated trading bot.
- A brokerage app.
- A real-money trade execution system.
- A guaranteed financial advice tool.

The MVP should focus on long-term investment research, with light support for swing trading analysis.

Product identity:

> A beginner-friendly AI investment research assistant that helps users understand the market, analyze holdings, and make more informed investment decisions.

---

## 2. Learning Goal

This is the user's first serious full-stack development project.

The implementation should teach and document normal professional workflow while building the app. Do not assume the user already knows:

- Git/GitHub workflow
- branches, commits, pull requests, and `main`
- Python virtual environments
- dependency management
- Docker Compose
- CI/CD
- Alembic migrations
- linting and formatting
- automated tests
- local development vs deployment

The project should be implemented like a real application, but explanations and docs should stay beginner-friendly.

---

## 3. MVP Scope

Version 0 is a local-first full-stack web application.

The MVP should eventually support:

- Single local user
- Holdings management
- Watchlist management
- Market data display
- Basic stock chart display
- On-demand AI report generation
- Individual stock analysis
- Portfolio and watchlist analysis
- Investment-focused chat assistant
- Local settings for API keys and model configuration
- Report or chat export, preferably Markdown

The MVP should not support:

- Multi-user public deployment
- Brokerage connection
- Real-money trade execution
- Automated trading
- Options, futures, crypto, or forex
- Advanced quantitative backtesting
- Subscription or payment system
- Email report delivery
- Mobile or desktop app adaptation
- Internal stock prediction model training

---

## 4. Main Pages

The MVP should eventually include:

- Dashboard
- Holdings
- Watchlist
- Stock Detail
- Reports
- Chat
- Settings

Phase 2 does not implement these product pages beyond existing Phase 1 health/dashboard scaffolding.

Phase 2 should focus on backend foundation and database readiness.

---

## 5. Architecture

Use a production-ish modular monolith.

Recommended stack:

- Frontend: Next.js App Router + React + TypeScript + Tailwind CSS + shadcn/ui
- Backend: FastAPI + Python + Pydantic + SQLAlchemy + Alembic
- Database: PostgreSQL
- AI integration: backend-managed OpenAI-compatible client
- Infrastructure: Docker + docker-compose + environment variables

High-level architecture:

```txt
User Browser
    -> Next.js React Frontend
    -> FastAPI Backend
    -> Application Modules
        -> Holdings
        -> Watchlist
        -> Market Data
        -> News
        -> Reports
        -> Chat
        -> AI
    -> PostgreSQL

External APIs
    -> Market Data API
    -> News API
    -> LLM API
```

Frontend must not directly call:

- LLM APIs
- Market data provider APIs
- News APIs
- Database

All external API and database access should go through FastAPI.

---

## 6. Locked Stack Decisions

### Frontend

- Next.js App Router
- React
- TypeScript
- pnpm
- Tailwind CSS
- shadcn/ui
- lucide-react
- TanStack Query
- React Hook Form
- Zod
- Lightweight Charts
- react-markdown

Migration-safe frontend rules:

- Wrap charts in `components/charts/StockPriceChart.tsx`.
- Wrap Markdown reports in `components/reports/MarkdownReport.tsx`.
- Keep backend API calls in `lib/api/`.
- Keep TanStack Query hooks in `lib/queries/`.
- Keep Zod schemas in `lib/schemas/`.
- Keep shared frontend business types in `types/`.
- Use simple `shadcn/ui` table components first.
- Delay TanStack Table until table requirements become complex.

### Backend

- Python 3.12+
- uv
- FastAPI
- Uvicorn
- Pydantic v2
- pydantic-settings
- SQLAlchemy 2.x sync ORM
- Alembic
- PostgreSQL
- psycopg 3
- pytest
- Ruff

Use `uv`, not Poetry.

Use synchronous SQLAlchemy first. Async database access can wait until there is a clear need.

### LLM

Use DeepSeek first through an OpenAI-compatible LLM client wrapper.

Keep LLM settings configurable:

```txt
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

Do not hardcode DeepSeek into business modules.

### v0 Defaults

- Use Markdown-only reports first.
- Use synchronous report generation first.
- Avoid Redis in v0.
- Avoid RAG and agents in v0.
- Use simple context injection first.
- Use `yfinance` only as prototype fallback.
- Use no authentication in v0 because the app is single-user and local-first.
- Use local Docker Compose only for v0 runtime.

---

## 7. Implementation Repo Structure

Implementation repo name:

```txt
ai-stock-analyst
```

Expected structure:

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
├── AGENTS.md
└── README.md
```

The Obsidian planning folder remains separate from the implementation repo.

---

## 8. Current Progress

### Phase 1: Complete

Phase 1 acceptance criteria:

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

### Phase 2: Active

Phase 2 goal:

Build the backend foundation before implementing complex product features.

Phase 2 should make the backend ready for real modules such as Holdings, Watchlist, Reports, Chat, Market Data, News, and AI.

Current build priority:

1. Confirm backend app structure is clean.
2. Confirm environment config is loaded through `pydantic-settings`.
3. Connect FastAPI backend to PostgreSQL.
4. Set up SQLAlchemy 2.x sync ORM.
5. Set up Alembic migrations.
6. Create initial database models and first migration.
7. Add core error handling and basic logging.
8. Add backend tests for health/config/database behavior where useful.
9. Keep documentation updated for beginner full-stack workflow.

Do not start Holdings and Watchlist CRUD yet.

---

## 9. Phase 2 Detailed Plan

### Phase 2.1: Review Existing Backend Structure

Tasks:

- [ ] Confirm `backend/` uses `uv`, `pyproject.toml`, and `uv.lock`.
- [ ] Confirm FastAPI entrypoint is clear.
- [ ] Confirm health module is separated from future business modules.
- [ ] Confirm backend tests can run with `uv run pytest`.
- [ ] Confirm linting can run with `uv run ruff check .`.

Success criteria:

- Backend structure is understandable.
- Basic commands are documented.
- The project is ready for database wiring.

### Phase 2.2: Core Configuration

Tasks:

- [ ] Create or refine `app/core/config.py`.
- [ ] Use `pydantic-settings` for environment variables.
- [ ] Load database URL from environment variables.
- [ ] Keep secrets out of committed files.
- [ ] Keep `.env.example` updated.

Expected settings:

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

Success criteria:

- Backend configuration is typed.
- Missing or invalid configuration fails clearly.
- Local Docker Compose environment can provide required database settings.

### Phase 2.3: Database Connection

Tasks:

- [ ] Create or refine `app/core/database.py`.
- [ ] Configure SQLAlchemy engine using sync ORM style.
- [ ] Configure session dependency for FastAPI routes and services.
- [ ] Use `psycopg` 3 as the PostgreSQL driver.
- [ ] Confirm backend can connect to Docker PostgreSQL.

Success criteria:

- Backend can connect to PostgreSQL.
- Database session creation is centralized.
- Future modules can reuse the same database dependency.

### Phase 2.4: Alembic Setup

Tasks:

- [ ] Initialize Alembic if not already done.
- [ ] Configure Alembic to read the same database URL/settings.
- [ ] Configure model metadata for autogeneration.
- [ ] Create initial migration.
- [ ] Document migration commands.

Expected commands:

```bash
uv run alembic revision --autogenerate -m "create initial tables"
uv run alembic upgrade head
uv run alembic downgrade -1
```

Success criteria:

- Alembic can generate migrations.
- Alembic can apply migrations to local PostgreSQL.
- Migration workflow is documented for the user.

### Phase 2.5: Initial Database Models

Initial tables:

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

Tasks:

- [ ] Create SQLAlchemy base model conventions.
- [ ] Create initial SQLAlchemy models.
- [ ] Add common fields where appropriate, such as `id`, `created_at`, and `updated_at`.
- [ ] Keep models simple; do not implement full business logic yet.
- [ ] Generate and apply migration for initial tables.

Success criteria:

- Basic tables can be created in PostgreSQL.
- Models are ready for Phase 3 CRUD work.
- No Holdings or Watchlist API CRUD implementation is required yet.

### Phase 2.6: Core Error Handling and Logging

Tasks:

- [ ] Create or refine `app/core/errors.py`.
- [ ] Add a consistent API error response pattern.
- [ ] Add basic exception handling for expected application errors.
- [ ] Avoid leaking secrets or internal stack traces in normal API responses.
- [ ] Create or refine `app/core/logging.py`.
- [ ] Configure basic structured or readable application logging.
- [ ] Ensure startup/database/config errors are easy to diagnose during local development.

Success criteria:

- Backend has a clear place for shared error handling.
- Backend has a clear place for logging setup.
- Health/config/database failures are easier to debug.
- Error handling remains simple and does not over-engineer Phase 2.

### Phase 2.7: Backend Quality Checks

Tasks:

- [ ] Add or update backend tests for health endpoint.
- [ ] Add tests for error handling behavior if practical.
- [ ] Add a lightweight database connectivity test if practical.
- [ ] Run `uv run pytest`.
- [ ] Run `uv run ruff check .`.
- [ ] Run `uv run ruff format .` only if formatting changes are intended.
- [ ] Ensure GitHub Actions still passes.

Success criteria:

- Backend tests pass.
- Backend lint passes.
- CI remains green.

---

## 10. Phase 2 Documentation Updates Needed In Dev Repo

Before or while implementing Phase 2, update these dev repo files:

```txt
README.md
AGENTS.md
docs/development-workflow.md
docs/backend.md
.env.example
.github/workflows/ci.yml
docs/database.md
```

If `docs/database.md` does not exist, create it.

### README.md

Update current project status:

- Phase 1 complete.
- Phase 2 active.
- Current focus is backend/database foundation.
- Do not mention Holdings/Watchlist CRUD as current work yet.

Include or verify commands:

```bash
docker compose up --build
cd backend
uv sync
uv run pytest
uv run ruff check .
uv run alembic upgrade head
cd ../frontend
pnpm install
pnpm dev
pnpm build
```

### AGENTS.md

Add current agent guidance:

- Current phase is Phase 2.
- Do not implement Holdings/Watchlist CRUD until Phase 2 acceptance criteria are met.
- Keep FastAPI as backend owner of database, external APIs, AI, reports, chat, and secrets.
- Keep Next.js as frontend/UI only.
- Use `uv` for backend dependency and virtual environment workflow.
- Use `pnpm` for frontend dependency workflow.
- Use SQLAlchemy 2.x sync ORM and Alembic.
- Keep docs beginner-friendly.

### docs/development-workflow.md

Add Phase 2 workflow explanations:

- What PostgreSQL does in this app.
- What SQLAlchemy does.
- What Alembic does.
- What a migration is.
- What basic backend error handling does.
- What backend logging is used for.
- How to create and apply migrations.
- How `.env` and `.env.example` work.
- How to run tests and lint checks before committing.

### docs/backend.md

Create or update with:

- FastAPI project structure.
- Modular monolith backend module convention.
- Core config approach with `pydantic-settings`.
- Core database dependency approach.
- Core error handling approach.
- Basic logging setup.
- Health endpoint purpose.

### .env.example

Verify these variables exist:

```txt
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL
BACKEND_CORS_ORIGINS
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

### .github/workflows/ci.yml

Ensure CI checks at least:

- Backend dependencies install with `uv sync`.
- Backend lint passes with `uv run ruff check .`.
- Backend tests pass with `uv run pytest`.
- Frontend dependencies install with `pnpm install`.
- Frontend build or type check passes.

### docs/database.md

Create or update with:

- PostgreSQL role in the app.
- SQLAlchemy sync ORM decision.
- psycopg 3 driver decision.
- Alembic migration workflow.
- Phase 2 initial table list.
- Common commands.

---

## 11. Phase 2 Acceptance Criteria

Phase 2 is complete when:

- [ ] Backend connects to PostgreSQL.
- [ ] SQLAlchemy 2.x sync ORM is configured.
- [ ] Alembic migrations work.
- [ ] Initial database tables can be created.
- [ ] Health check endpoint still works.
- [ ] Core error handling structure exists.
- [ ] Basic logging setup exists.
- [ ] Backend structure follows modular monolith design.
- [ ] Backend tests pass.
- [ ] Backend lint passes.
- [ ] Database and migration workflow is documented.

Only after this should the project move to Phase 3: Holdings and Watchlist CRUD.

---

## 12. Next Codex Session Prompt

Paste this file into the dev repo session and say:

```txt
Use this merged Phase 2 handoff as the current source of truth.

We are now in Phase 2: Backend and Database Foundation.

First update the dev repo guide/docs to reflect Phase 2:

- README.md
- AGENTS.md
- docs/development-workflow.md
- docs/backend.md
- .env.example
- .github/workflows/ci.yml if needed
- docs/database.md

Then implement Phase 2 only:

- backend structure review
- pydantic-settings config
- PostgreSQL connection
- SQLAlchemy 2.x sync ORM
- Alembic migrations
- core error handling
- basic logging
- initial database models
- backend tests
- Ruff checks

Do not implement Holdings/Watchlist CRUD yet.
Do not build unrelated future features yet.
```
