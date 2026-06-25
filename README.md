# AI Stock Analyst

AI Stock Analyst is a local-first AI-powered stock research assistant. Version 0 starts with a professional full-stack foundation and grows toward holdings, watchlist, market data, AI reports, and chat in later phases.

This project is for investment research and decision support only. It is not a trading bot, brokerage app, real-money execution system, or guaranteed financial advice tool.

## Current Status

Phases 0–2 are complete.

Current active phase: **Phase 3: Holdings and Watchlist CRUD**.

Phase 3 builds the first real product features on the Phase 2 foundation: manual CRUD for Holdings and Watchlist items, end to end (backend `router → service → repository` + Pydantic schemas, plus frontend pages). It does not implement market data or AI yet. See [Roadmap & Progress](docs/roadmap.md) for the detailed current-phase scope.

Completed in Phases 0–2:

- Planning and design (charter, vision, requirements, architecture, AI design, decisions)
- FastAPI backend health endpoint and Next.js dashboard health check
- PostgreSQL Docker service and Docker Compose local stack
- Typed `pydantic-settings` config, SQLAlchemy 2.x models, Alembic migrations (8 initial tables)
- Core error handling, logging, and backend tests
- Basic GitHub Actions CI

Project docs:

- [Roadmap & Progress](docs/roadmap.md)
- [Backend Guide](docs/guides/backend.md)
- [Database Guide](docs/guides/database.md)
- [Development Workflow](docs/guides/development-workflow.md)

In progress:

- Holdings CRUD
- Watchlist CRUD

Not started yet:

- Market data integration
- News integration
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

Alembic migration commands:

```bash
uv run alembic upgrade head
uv run alembic downgrade -1
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
- `BACKEND_CORS_ORIGINS`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
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

For Phase 2 feature work, create a branch from `main`:

```bash
git checkout main
git pull
git checkout -b phase-2/backend-database-foundation
```

When the work is ready, push the branch and open a pull request on GitHub.

## CI

GitHub Actions runs basic checks when code is pushed or a pull request is opened:

- backend dependency install
- backend Ruff lint
- backend pytest tests
- frontend dependency install
- frontend typecheck
- frontend build

CI helps catch errors before code is merged into `main`.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
