# Changelog

Build history by phase. The active phase and its detailed scope live in `docs/roadmap.md`; this file is the frozen record of what was completed. Per the Per-phase handoff rules in `CLAUDE.md`, append a new section here when a phase is finished.

## Phase 3 — Holdings and Watchlist CRUD (done 2026-06-25)

- Built: full manual CRUD for **Holdings** and **Watchlist**, end to end. Backend `router → service → repository` modules + Pydantic v2 `schemas` for both (Create/Update/Read split, ticker trim+uppercase normalization, `shares > 0` / `average_cost >= 0` / `target_allocation` 0–1 validation), service-layer not-found → `AppError(404)`, both routers registered in `app/main.py`. SQLite-backed test suite (20 tests: CRUD + 404 + 422 per module) via a `get_db` dependency override. Frontend: a shared `apiFetch` helper, typed `holdings`/`watchlist` API clients, and `/holdings` + `/watchlist` pages with create/edit/delete and loading/error/empty states, plus dashboard nav links.
- Files: `backend/app/modules/holdings/{__init__,schemas,repository,service,router}.py`, `backend/app/modules/watchlist/{__init__,schemas,repository,service,router}.py`, `backend/app/main.py` (router registration), `backend/tests/{conftest,test_holdings,test_watchlist}.py`; `frontend/lib/api/{client,holdings,watchlist}.ts`, `frontend/app/holdings/page.tsx`, `frontend/app/watchlist/page.tsx`, `frontend/app/page.tsx` (nav); docs (`docs/guides/{backend,database,api}.md`).
- Key decisions: partial updates use **`PATCH`** (not `PUT`); `target_allocation` stored as a **fraction (0–1)** to match computed allocation; **SQLite in-memory** test DB (no Docker in CI) via `get_db` override; **no new migration** — the `holdings`/`watchlist_items` tables were unchanged from Phase 2; `Decimal` is serialized over the wire as a **string**, so frontend types numeric fields as `string`.

## Phase 2 — Backend and Database Foundation (done 2026-06-20)

- Built: typed `pydantic-settings` config (`core/config.py`), PostgreSQL connection + `get_db` session dependency (`core/database.py`), SQLAlchemy 2.x sync ORM base/`TimestampMixin`, Alembic migration setup, the 8 initial tables, a shared `AppError` error-handling pattern (`core/errors.py`), basic logging setup (`core/logging.py`), and backend tests (health, error handling, database connectivity).
- Files: `backend/app/core/{config,database,errors,logging}.py`, `backend/app/models/` (one file per table, re-exported in `models/__init__.py`), `backend/alembic/` + `backend/alembic/versions/faff5d463169_create_initial_tables.py`, `backend/tests/`.
- Initial tables: `holdings`, `watchlist_items`, `reports`, `chat_sessions`, `chat_messages`, `stock_notes`, `market_data_cache`, `settings` (all inherit `TimestampMixin`).
- Key decisions: synchronous SQLAlchemy 2.x (`Mapped[...]` style) over async; `psycopg` 3 driver; all models centralized in `backend/app/models/` (not per-module); schema changes go through Alembic only — never hand-edit the initial migration; secrets in a root `.env` loaded by `config.py`.

## Phase 1 — Repository and Development Environment Setup (done 2026-06-18)

- Built: initial repository skeleton (`frontend/`, `backend/`, `docs/`, `prompts/`, `scripts/`), FastAPI backend `GET /api/health` endpoint, Next.js dashboard that calls the health endpoint, PostgreSQL Docker service, full Docker Compose local stack (frontend / backend / postgres), and basic GitHub Actions CI.
- Files: `docker-compose.yml`, `.env.example`, `.gitignore`, `backend/` (FastAPI skeleton + `health/` module + `Dockerfile`), `frontend/` (Next.js App Router skeleton + `lib/api/` + `Dockerfile`), `.github/workflows/` CI, draft `README.md`, `docs/development-workflow.md`.
- Key decisions: modular monolith; backend owns all external access (DB, market/news APIs, LLM, secrets), frontend is presentation-only and talks only to the backend REST API; `uv` for backend, `pnpm` for frontend; local-first, no auth in v0.

## Phase 0 — Planning and Design (done 2026-06-17)

- Built: the project's design brain — charter, vision, requirements, user stories, architecture, data sources, AI design, roadmap, decisions, and open questions.
- Files: `docs/planning/` (`charter.md`, `vision.md`, `requirements.md`, `user-stories.md`, `architecture.md`, `data-sources.md`, `ai-design.md`, `decisions.md`, `open-questions.md`) and `docs/roadmap.md`.
- Key decisions: local-first single-user AI stock **research** assistant (not a trading/brokerage/execution system); phase-by-phase build order; MVP uses simple DB-context injection for the LLM (RAG and agents explicitly deferred); OpenAI-compatible LLM client (DeepSeek first).
