# Development Workflow

This document explains the professional workflow for AI Stock Analyst in beginner-friendly terms.

## Current Phase

Phase 1 is complete. The active phase is **Phase 2: Backend and Database Foundation**.

Phase 2 does not build Holdings/Watchlist CRUD yet. It prepares the backend and database so those features can be added safely in the next phase.

Use these docs during Phase 2:

- [Phase 2 Plan](phase-2-plan.md)
- [Backend Guide](backend.md)
- [Database Guide](database.md)

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

For Phase 2 work, create a separate branch:

```bash
git checkout main
git pull
git checkout -b phase-2/backend-database-foundation
```

This keeps unfinished backend/database work separate from the stable `main` branch.

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

Type check:

```bash
pnpm typecheck
```

Build:

```bash
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

Phase 2 should keep `.env.example` updated whenever new backend settings are introduced.

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

An ORM maps Python classes to database tables. In Phase 2, SQLAlchemy models define the first table shapes. Business features and CRUD routes come later.

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

Backend error handling gives the API a consistent way to return errors.

Phase 2 should add a simple shared error structure so future modules can raise predictable application errors without leaking secrets or raw stack traces to normal API clients.

## Backend Logging

Logging records useful backend events during local development.

Phase 2 should add a basic logging setup so startup, configuration, database, and API issues are easier to diagnose.

## pytest

`pytest` runs backend tests:

```bash
cd backend
uv run pytest
```

Tests protect the app from breaking when code changes.

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

- backend dependencies install
- backend Ruff lint
- backend pytest tests
- frontend dependencies install
- frontend typecheck
- frontend build

CI does not deploy the app yet.

## Local Development vs Deployment

Local development means running the app on your computer.

Deployment means running the app on a server for users.

Version 0 is local-first. Docker Compose is for local development, not production deployment yet.
