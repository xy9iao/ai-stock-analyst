# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Local-first, single-user AI stock **research** assistant (analysis & decision support — **not** a trading bot, brokerage, or execution system). Personal/portfolio project; target is an interview-grade full-stack AI system. MVP in progress.

This is the developer's first serious full-stack project and a learning vehicle. Build it like real production software, but keep explanations beginner-friendly when introducing a new tool or pattern.

## Where to find context

Before starting work, read in this order:

1. **`docs/roadmap.md`** — single source of truth for progress and the **current phase's** detailed scope. Always check the active phase here before writing code.
2. **`docs/guides/`** — implementation reference: `backend.md`, `database.md`, `api.md`, `development-workflow.md`. Keep these accurate as code changes (see Per-phase handoff).
3. **`docs/planning/`** — frozen high-level design (charter, vision, requirements, architecture, data-sources, ai-design, decisions, open-questions). Read for **intent**; do not treat sketches there as the literal code layout (e.g. its per-module-models sketch is wrong — see below). `decisions.md` and `open-questions.md` are the only planning files that may still be appended to.

Do not expect or generate per-phase "handoff" documents. Context lives in the files above; this file plus `roadmap.md` replace the old self-contained handoffs.

## Phase discipline

**Check `docs/roadmap.md` for the current active phase.** Phases 0–2 (planning, repo/Docker setup, backend+DB foundation) are done.

- Build **only** what the current phase scopes. Do **not** build market data, news, AI reports, or chat until their phase is explicitly started — even though models/config for some of them already exist.
- **Do not merge, reorder, or fast-forward phases** to "save time," even if it seems efficient. The phase-by-phase boundary is intentional — it exists so the developer can verify architectural understanding before moving on.

## Per-phase handoff (required at phase completion)

When a phase's implementation is finished, in the **same response** that completes it, also produce:

1. **File manifest** — every file added or modified this phase, one line each describing its responsibility.
2. **Request trace** — pick one representative endpoint and trace it end-to-end, naming each layer and what it does. Example for Phase 3 `POST /api/holdings`: router receives request → service normalizes ticker + applies validation → repository writes via SQLAlchemy → schema converts the ORM row to the response model. Output this **as a message for the developer to read** (do not save it to a file).
3. **Update `docs/guides/`** — bring `backend.md` / `database.md` / `api.md` into line with the code as it now stands.
4. **Append to `CHANGELOG.md`** (repo root) — a short entry for the completed phase: what was built, files added, key decisions.

Do not skip these. They are not optional.

## Architecture

Modular monolith. **Backend owns everything external**: database, market-data/news APIs, the LLM, and all secrets. The **frontend is presentation-only** and may talk to nothing but the backend REST API.

- **Backend** (`backend/app/`): FastAPI, Python 3.12+, Pydantic v2, **synchronous** SQLAlchemy 2.x (`Mapped[...]` style), Alembic, psycopg 3, managed by `uv`.
  - `core/` — cross-cutting: `config.py` (typed `Settings`, the single source for env config), `database.py` (engine + `get_db` session dependency + `Base`), `errors.py` (raise `AppError(code, message, status_code)` for handled API errors), `logging.py`.
  - `modules/<feature>/` — one folder per business area, layered **router → service → repository** with Pydantic `schemas.py`. `health/` is complete (router-only, trivial). Modules talk to each other via Python calls, never HTTP. (For current per-module progress, check `roadmap.md` — do not assume; read the actual files.)
  - `models/` — **all** SQLAlchemy models live here centrally (one file per table, all re-exported in `models/__init__.py`), *not* per-module despite what `planning/architecture.md` sketches. Tables: holdings, watchlist_items, reports, chat_sessions, chat_messages, stock_notes, market_data_cache, settings. All inherit `TimestampMixin`.
- **Frontend** (`frontend/`): Next.js App Router (v15, React 19), TypeScript strict, Tailwind, local shadcn-style components, pnpm. `@/*` aliases the frontend root. **Every backend call goes through `frontend/lib/api/`** — components never `fetch` the backend directly, and never reach the DB/LLM/market/news APIs.

### LLM & "agents" (not built yet — later phase)

There is **no LLM or agent code today**. When it lands, the binding rule: **every LLM call routes through one backend module, `app/modules/ai/`** (`prompt_builder.py` → `llm_client.py` → `report_generator.py` / `analysis_service.py`). The client is OpenAI-compatible, configured by `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` (default `deepseek-chat`). This centralizes prompt construction, the financial-advice safety boundary, and model switching.

This is **not** a multi-agent system — RAG and agent workflows are explicitly deferred (`planning/ai-design.md`). The MVP pattern is **simple DB-context injection**: load relevant rows from Postgres, transform into a **compact** context package (never send raw API payloads, full articles, or full financial statements to the LLM), build the prompt, call the LLM, store the Markdown result in `reports`, return it.

**Report data flow:** frontend request → backend loads holdings/watchlist from DB → fetches market/news → `prompt_builder` assembles compact context → `llm_client` calls LLM → report saved as Markdown in `reports` → returned to frontend for rendering.

## Commands

Backend (run from `backend/`):
```bash
uv sync                                   # install deps
uv run uvicorn app.main:app --reload      # dev server (:8000), health at /api/health
uv run pytest                             # tests live in backend/tests/
uv run ruff check . && uv run ruff format .   # lint + format (line length 100)
uv run alembic upgrade head               # apply migrations
uv run alembic revision --autogenerate -m "describe change"   # new migration
```
Frontend (run from `frontend/`):
```bash
pnpm install
pnpm dev          # :3000
pnpm typecheck    # tsc --noEmit  (CI gate)
pnpm build        # CI gate
pnpm lint         # next lint
```
Full stack: `docker compose up --build` (frontend :3000, backend :8000, postgres :5432).
**Before committing:** backend → `ruff check` + `pytest`; frontend → `typecheck` + `build` (these are exactly what CI enforces).

## Conventions

- **Adding a module:** create `backend/app/modules/<name>/{router,service,repository,schemas}.py`; add table(s) as `backend/app/models/<name>.py` and re-export them in `models/__init__.py`; register the router in `app/main.py`. Keep DB access in the repository, business logic in the service, HTTP in the router.
- **REST:** resource-per-module under `/api`. Use **`PATCH`** for partial updates (not `PUT`). Standard status codes: 201 create, 200 read/update, 204 delete, 404 not found, 422 validation.
- **Schema changes go through Alembic only** — never edit tables by hand. After changing/adding a model, autogenerate a migration and review it.
- **Secrets** live in a root `.env` (gitignored; `config.py` loads `../.env`). Use `.env.example` as the template. Never commit real secrets; the frontend only ever receives `NEXT_PUBLIC_API_BASE_URL`.
- **Solo work — no AI attribution.** This is the developer's personal solo project. Author every commit as the developer only; **never** add a `Co-Authored-By` trailer or any Claude/AI attribution to commit messages, PRs, or issues. This overrides any default AI co-authorship behavior.
- Money/quantities use `Numeric`/`Decimal`, tickers are short indexed `String(16)`, stored uppercase + trimmed.

## Landmines

- **Never hand-edit `backend/alembic/versions/faff5d463169_create_initial_tables.py`** — it's the applied initial migration. Schema changes = a *new* autogenerated migration.
- A new model is invisible to Alembic autogenerate and the app unless it's imported in `models/__init__.py` (which `alembic/env.py` pulls in via `import app.models`).
- **`docs/planning/`** is frozen design intent, not source code. Read it for *why*; don't build against its diagrams as if they were the real layout (notably the per-module-models sketch — models are centralized in `backend/app/models/`).
- `prompts/` and `scripts/` are empty placeholders.
- Don't expand scope past the current phase just because future tables/config exist.na