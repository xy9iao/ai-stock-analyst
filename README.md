# AI Stock Analyst

AI Stock Analyst is a local-first AI-powered stock research assistant. Version 0 begins with a professional full-stack foundation: a Next.js frontend, a FastAPI backend, a PostgreSQL database, Docker Compose for local development, and basic CI checks.

This project is for investment research and decision support only. It is not a trading bot, brokerage app, real-money execution system, or guaranteed financial advice tool.

## Current Status

Phase 1 is the only active phase.

Completed:

- FastAPI backend health endpoint
- Next.js dashboard
- Frontend-to-backend health check
- PostgreSQL Docker service
- Docker Compose local stack
- Alembic migration foundation

Not started yet:

- Holdings CRUD
- Watchlist CRUD
- Market data
- News data
- AI reports
- Chat

## Tech Stack

Backend:

- Python 3.12+
- uv
- FastAPI
- Pydantic v2
- pydantic-settings
- SQLAlchemy 2.x sync style
- Alembic
- psycopg 3
- pytest
- Ruff

Frontend:

- Next.js App Router
- React
- TypeScript
- pnpm
- Tailwind CSS
- shadcn/ui-style local components
- lucide-react

Infrastructure:

- PostgreSQL
- Docker Compose
- GitHub Actions CI

## Local Setup

Clone the repository:

```bash
git clone https://github.com/xy9iao/ai-stock-analyst.git
cd ai-stock-analyst
```

Install required tools:

```bash
brew install uv
corepack enable
corepack prepare pnpm@11.6.0 --activate
```

Copy environment variables:

```bash
cp .env.example .env
```

The `.env` file is local only. Do not commit real secrets.

## Docker Compose

Start the full local stack:

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Backend health: http://localhost:8000/api/health
- PostgreSQL: localhost:5432

Stop the stack with `Ctrl+C`.

## Backend Commands

Run commands from `backend/`:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format .
```

Alembic migration commands for future database changes:

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe change"
```

## Frontend Commands

Run commands from `frontend/`:

```bash
cd frontend
pnpm install
pnpm dev
pnpm typecheck
pnpm build
```

## Environment Variables

See `.env.example`.

Important variables:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`
- `NEXT_PUBLIC_API_BASE_URL`

In Docker Compose, the frontend uses `http://backend:8000` to reach the backend container. In local browser development, use `http://localhost:8000`.

## Git and GitHub Workflow

Use small commits for working checkpoints:

```bash
git status
git add .
git commit -m "Short description of change"
git push
```

For future feature work, create a branch from `main`:

```bash
git checkout main
git pull
git checkout -b feature/holdings-crud
```

When the feature is ready, push the branch and open a pull request on GitHub.

## CI

GitHub Actions will run basic checks when code is pushed or a pull request is opened:

- backend dependency install
- backend Ruff lint
- backend pytest tests
- frontend dependency install
- frontend typecheck
- frontend build

CI helps catch errors before code is merged into `main`.
