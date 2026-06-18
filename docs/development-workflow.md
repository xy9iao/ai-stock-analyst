# Development Workflow

This document explains the basic professional workflow for AI Stock Analyst.

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

## Main Branch

`main` is the stable branch. Code on `main` should work.

For future features, create a separate branch:

```bash
git checkout main
git pull
git checkout -b feature/short-feature-name
```

## Commits

A commit is a saved checkpoint.

Good commits are small and focused. Examples:

```txt
Add backend health endpoint
Add Docker Compose local stack
Add frontend dashboard health check
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

## PostgreSQL

PostgreSQL is the application database.

In local Docker Compose, it runs on:

```txt
localhost:5432
```

The backend uses `DATABASE_URL` to connect to it.

## Alembic

Alembic manages database schema migrations.

A migration is a versioned database change. Phase 1 only adds the Alembic foundation. Real table migrations come later.

Run migrations:

```bash
cd backend
uv run alembic upgrade head
```

Create a migration after adding models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

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

Phase 1 CI checks:

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
