# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Local-first, single-user AI stock **research** assistant (analysis & decision support — **not** a trading bot, brokerage, or execution system). Personal/portfolio project; target is an interview-grade full-stack AI system. **v0 is shipped and frozen** (`v0.1.0`, live demo at https://ai-stock-analyst-pi.vercel.app; demo hardening: `DEMO_MODE` anonymous sessions + three-layer LLM cost defense + `llm_calls`/`/api/stats` observability — `docs/guides/deployment.md`). **v1 — Agent Layer (Phases 13–15) is complete (2026-07-21)** — Research Agent, hybrid RAG + cited reports, compression + injection defense, all scoped in `docs/roadmap.md`. The project is now in **demand-gated maintenance**; Phase 13.5 (local MCP wrapper) was descoped to an optional post-v1 add-on. **Maintenance gate (binding):** any change to prompts, models, or retrieval/compression parameters must run `backend/eval/` (`uv run python -m eval.run`, plus `--citations` / `--poisoned`) before merge; a regression below baseline − tolerance blocks. New feature ideas go to GitHub issues, built only when the same need recurs.

This is the developer's first serious full-stack project and a learning vehicle. Build it like real production software, but keep explanations beginner-friendly when introducing a new tool or pattern.

## Where to find context

Before starting work, read in this order:

1. **`docs/roadmap.md`** — single source of truth for progress and the **current phase's** detailed scope. Always check the active phase here before writing code.
2. **`docs/guides/`** — implementation reference: `backend.md`, `database.md`, `api.md`, `frontend.md`, `development-workflow.md`. Keep these accurate as code changes (see Phase close-out).
3. **`docs/planning/`** — high-level design (charter, vision, requirements, architecture, data-sources, ai-design, decisions, open-questions), each carrying a **v0-outcome note** at the top. Read for **intent**; do not treat sketches there as the literal code layout (e.g. its per-module-models sketch is wrong — see below). This folder is also where the **next version** will be planned.

Do not create per-phase "handoff" documents — the active plan lives in `docs/roadmap.md`, and context lives in the files above.

## Phase discipline

**Check `docs/roadmap.md` for status.** v0 (Phases 0–12) is frozen; **v1 = Phases 13–15 is complete (2026-07-21)**; Phase 13.5 (MCP) is an optional post-v1 add-on, unscheduled. Project is in demand-gated maintenance. Binding v1 rules (still apply to any maintenance work): no agent frameworks (Decision 010), routing by request type is a design decision and chat stays non-agentic (Decision 011), no new LLM code paths outside `llm_client`, hybrid retrieval and injection-defense depth per Decisions 012–013.

- Build **only** what the active phase (or an explicitly assigned GitHub issue) scopes. Do **not** add new features to v0 — deferred ideas live as issues (#14 Home news/financials, #15 ticker autocomplete, #16 E2E).
- **Do not merge, reorder, or fast-forward phases** to "save time," even if it seems efficient. The phase-by-phase boundary is intentional — it exists so the developer can verify architectural understanding before moving on.
- **Plan first:** for any phase or feature, draft a plan and get the developer's confirmation before writing code.

## Learning-Gated Development (v1+, binding)

Every v1 phase plan declares its work in two tiers (the split lives in that phase's `docs/roadmap.md` section). **Core** is the interview-walkable logic. CC guides it in separated steps — design lesson first, then a complete solution with rationale — and the owner reviews it, asks questions, and **personally enters the code** (typed or pasted). CC touches core files only in the final cleanup pass — senior-SWE rewrites allowed, but every improvement must be shown as a diff and explained to the owner. **Periphery** (wiring, migrations, frontend rendering, glue, scaffolding, config) is CC-written under normal review. **Regression gate:** once the Phase 13 regression set lands in `eval/`, any change to prompts, models, or retrieval parameters runs it before merge — a score drop blocks the merge.

The full workflow — kickoff, teach mode, cleanup, merge gate, close-out — is the local **`teaching` skill** (`.claude/skills/teaching/SKILL.md`, gitignored). **Follow it for any v1 core work.** Career material lives in the gitignored `interview-defense.md` — **update its defense blocks after each phase** — and is never committed or copied into tracked files or PR bodies.

## Phase close-out (required at phase completion)

When a phase's implementation is finished, in the **same response** that completes it: sync the docs and append the CHANGELOG entry per the **Phase Close-Out checklist in `docs/guides/development-workflow.md`**, and produce the teaching close-out per the `teaching` skill — file manifest, request trace, and **updating `interview-defense.md`'s defense blocks for the phase**. Not optional.

## Architecture

Modular monolith. **Backend owns everything external**: database, market-data/news APIs, the LLM, and all secrets. The **frontend is presentation-only** and may talk to nothing but the backend REST API.

- **Backend** (`backend/app/`): FastAPI, Python 3.12+, Pydantic v2, **synchronous** SQLAlchemy 2.x (`Mapped[...]` style), Alembic, psycopg 3, managed by `uv`.
  - `core/` — cross-cutting: `config.py` (typed `Settings`, the single source for env config), `database.py` (engine + `get_db` session dependency + `Base`), `errors.py` (raise `AppError(code, message, status_code)` for handled API errors), `logging.py`.
  - `modules/<feature>/` — one folder per business area, layered **router → service → repository** with Pydantic `schemas.py`. All eight v0 modules are built: `health`, `holdings`, `watchlist`, `market_data`, `news`, `financials`, `ai`, `chat`. The three data modules add a `provider.py` (`typing.Protocol`) + `providers/` (yfinance implementations, selected by config, cached via `core/cache.py`). Modules talk to each other via Python calls, never HTTP.
  - `models/` — **all** SQLAlchemy models live here centrally (one file per table, all re-exported in `models/__init__.py`), *not* per-module despite what `planning/architecture.md` sketches. Tables: holdings, watchlist_items, reports, chat_sessions, chat_messages, stock_notes, market_data_cache, settings. All inherit `TimestampMixin`.
- **Frontend** (`frontend/`): Next.js App Router (v15, React 19), TypeScript strict, Tailwind, local shadcn-style components, pnpm. `@/*` aliases the frontend root. **Every backend call goes through `frontend/lib/api/`** — components never `fetch` the backend directly, and never reach the DB/LLM/market/news APIs.

### LLM & "agents"

The binding rule: **every LLM call routes through `app/modules/ai/llm_client.py`** — the single OpenAI-compatible call site (`chat()` multi-turn; `complete()` delegates to it), configured by `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` (default `deepseek-v4-flash`, DeepSeek). This centralizes prompt construction, the financial-advice safety boundary (in the system prompt), and model switching. The `ai/` module: `context.py` (compact DB-context assembly) → `prompt_builder.py` → `llm_client.py` → `report_generator.py`; `chat/` reuses `ai/context` and the same client.

The v0 pattern is **simple DB-context injection**: load relevant rows from Postgres, transform into a **compact** context package (never send raw API payloads, full articles, or full financial statements to the LLM), build the prompt, call the LLM, store the Markdown result in `reports`, return it. **v1 adds an agent path on top** — the hand-written tool loop in `ai/agent/{loop,tools,indicators}.py` (roadmap Phase 13; Decisions 010/011) — but the binding rule is unchanged: every LLM call, pipeline or agent, goes through `llm_client`, and the `llm_calls` row records `route`/`steps`.

**Report data flow:** frontend request → backend loads holdings/watchlist from DB → fetches market/news → `prompt_builder` assembles compact context → `llm_client` calls LLM → report saved as Markdown in `reports` → returned to frontend for rendering.

## Commands

Backend (run from `backend/`):
```bash
uv sync                                   # install deps
uv run uvicorn app.main:app --reload      # dev server (:8000), health at /api/health
uv run pytest                             # tests live in backend/tests/ (prints coverage, not gated)
uv run ruff check . && uv run ruff format .   # lint + format (line length 100)
uv run alembic upgrade head               # apply migrations
uv run alembic revision --autogenerate -m "describe change"   # new migration
```
Frontend (run from `frontend/`):
```bash
pnpm install
pnpm dev          # :3000
pnpm typecheck    # tsc --noEmit  (CI gate)
pnpm lint         # eslint .  (CI gate)
pnpm test         # vitest run  (CI gate)
pnpm build        # CI gate
```
Full stack: `docker compose up --build` (frontend :3000, backend :8000, postgres :5432; runs migrations automatically). Day-to-day dev: `docker compose up postgres backend` + native `pnpm dev` (hot reload).
**Before committing:** backend → `ruff check` + `pytest`; frontend → `typecheck` + `lint` + `test` + `build` (these are exactly what CI enforces).

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
- `scripts/demo-llm.sh` operates the demo LLM switch (secret-free — reads `ADMIN_TOKEN`/`DEMO_API_URL` from the gitignored root `.env`).
- Don't expand scope past the current phase just because future tables/config exist — v0 is frozen; new ideas become GitHub issues.