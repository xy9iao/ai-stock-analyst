# Development Workflow

This document explains the professional workflow for AI Stock Analyst in beginner-friendly terms.

## Current Status

**v0 (MVP) and v1 (Agent Layer, Phases 13–15) are both complete (v1 done 2026-07-21).** The project is in **demand-gated maintenance** — a new feature requires the same need recurring 3+ times in real use. Check [`docs/roadmap.md`](../roadmap.md) for status and the binding maintenance gate (the `eval/` regression set runs before any prompt/model/retrieval change).

## The Two Development Loops

Day-to-day coding uses the **fast inner loop** — native dev servers with hot reload:

```bash
docker compose up postgres backend    # data layer in Docker
cd frontend && pnpm dev               # frontend natively, hot reload, /api proxied to :8000
```

`docker compose up --build` is the **slow outer loop**: images are frozen snapshots, so rebuilding takes minutes. Use it to verify the whole stack wires together (e.g. before a PR), not for every change.

## Git and GitHub

Git tracks changes in the project. GitHub stores a copy of the repository online.

Use `git status` often. It tells you what changed before you commit.

Common commands:

```bash
git status
git add .
git commit -m "Describe the change"
git push
```

## Branches

`main` is the stable branch. Code on `main` should work.

Every phase or fix gets its own branch, then a PR into `main`:

```bash
git checkout main && git pull
git checkout -b <topic-branch>      # e.g. phase-9-ui-polish, fix-lint
# ...work, commit, push, open a PR, merge...
git checkout main && git pull --ff-only
git fetch --prune origin && git branch -d <topic-branch>
```

This keeps unfinished work off `main` and gives every change a CI-checked review point.

## Commits

A commit is a saved checkpoint.

Good commits are small and focused. Examples:

```txt
Refine backend settings
Add database session dependency
Add initial database models
Add first Alembic migration
```

## Pull Requests

A pull request asks GitHub to merge one branch into another.

Even for a solo project, pull requests are useful because they:

- show what changed
- run CI checks
- create a review point
- keep `main` cleaner

## Phase Close-Out

When a phase's implementation is finished, close it out in the same response that completes it:

1. **Update `docs/guides/`** — bring `backend.md` / `database.md` / `api.md` (and `frontend.md` when the UI changed) into line with the code as it now stands.
2. **Append to `CHANGELOG.md`** (repo root) — a short entry for the completed phase: what was built, files added, key decisions.

This keeps the guides trustworthy (they describe the code as it exists) and the CHANGELOG the accurate build history.

## Python Virtual Environments

A Python virtual environment is a project-local Python environment. It prevents one project's packages from interfering with another project's packages.

This project uses `uv` to create and manage the backend virtual environment.

## uv

`uv` installs Python dependencies and runs backend commands inside the virtual environment.

Backend setup:

```bash
cd backend
uv sync
```

Run backend server:

```bash
uv run uvicorn app.main:app --reload
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Format code:

```bash
uv run ruff format .
```

## pnpm

`pnpm` installs frontend dependencies.

Frontend setup:

```bash
cd frontend
pnpm install
```

Run frontend server:

```bash
pnpm dev
```

The four frontend gates (all enforced by CI):

```bash
pnpm typecheck
pnpm lint
pnpm test        # Vitest + React Testing Library
pnpm build
```

## Docker Compose

Docker Compose runs multiple local services together.

This project uses Compose for:

- frontend
- backend
- PostgreSQL

Start everything:

```bash
docker compose up --build
```

Stop the stack with `Ctrl+C`.

## .env and .env.example

`.env.example` is committed to Git and documents required environment variables.

`.env` is local only and should never be committed. It can contain real local secrets or local overrides.

Create `.env` from the example:

```bash
cp .env.example .env
```

Keep `.env.example` updated whenever new settings are introduced.

## PostgreSQL

PostgreSQL is the application database.

In local Docker Compose, it runs on:

```txt
localhost:5432
```

The backend uses `DATABASE_URL` to connect to it.

The frontend must not connect directly to PostgreSQL. All database access goes through FastAPI.

## SQLAlchemy

SQLAlchemy is the Python ORM used by the backend.

An ORM maps Python classes to database tables. The SQLAlchemy models in `app/models/` define the table shapes; the module layers (service/repository/router) build CRUD on top of them.

This project uses SQLAlchemy 2.x sync style for v0.

## Alembic

Alembic manages database schema migrations.

A migration is a versioned database change. It lets the database evolve in a controlled way as models change.

Run migrations:

```bash
cd backend
uv run alembic upgrade head
```

Undo the latest migration:

```bash
uv run alembic downgrade -1
```

Create a migration after adding models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

## Backend Error Handling

Backend error handling gives the API a consistent way to return errors: `core/errors.py` provides `AppError` + a global handler that returns a stable JSON body without leaking secrets or stack traces (see [backend.md](backend.md)).

## Backend Logging

Logging records useful backend events. `core/logging.py` provides a simple shared setup so startup, configuration, database, and API issues are easy to diagnose (see [backend.md](backend.md)).

## pytest

`pytest` runs backend tests (with a coverage report — measured, not gated):

```bash
cd backend
uv run pytest
```

Tests use in-memory SQLite and mock all external providers/the LLM, so they need no network, no database, and no API key.

## Ruff

Ruff checks Python code style and common mistakes:

```bash
cd backend
uv run ruff check .
uv run ruff format .
```

Use `ruff check` before committing backend code.

## GitHub Actions CI

CI means continuous integration.

In this project, GitHub Actions automatically checks code after a push or pull request.

Current CI checks:

- backend: install → Ruff lint → pytest (with coverage report)
- frontend: install → typecheck → ESLint → Vitest → build

Run the same gates locally before committing.

CI gates every PR; Render and Vercel auto-deploy `main` on push — tests gate the merge, the merge is the deploy (see [deployment.md](deployment.md)).

## Local Development vs Deployment

Local development uses the two loops from the top of this guide: Docker Compose for the data layer, plus native dev servers with hot reload.

Deployment means running the app on a server for users. The public demo is deployed (Vercel + Render + Neon) — see [deployment.md](deployment.md).
