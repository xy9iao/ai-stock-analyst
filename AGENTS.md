# AGENTS.md

Stable instructions for future Codex sessions in AI Stock Analyst.

## Project Goal

AI Stock Analyst is a local-first AI-powered stock research assistant for investment research and decision support.

It is not:

- a trading bot
- a brokerage app
- a real-money execution system
- guaranteed financial advice

## Current Phase Rule

Current active phase: **Phase 2: Backend and Database Foundation**.

Phase 1 is complete. Phase 2 prepares backend structure, configuration, PostgreSQL connectivity, SQLAlchemy models, Alembic migrations, error handling, logging, tests, and documentation.

Do not implement Holdings CRUD, Watchlist CRUD, market data integration, news integration, AI reports, chat, authentication, deployment automation, or production infrastructure until Phase 2 acceptance criteria are complete and the user explicitly starts a later phase.

## Architecture Boundaries

Frontend:

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui-style local components
- lucide-react
- Calls backend APIs only through `frontend/lib/api/`
- Must not call the database, LLM APIs, market data APIs, or news APIs directly

Backend:

- FastAPI
- Python 3.12+
- Pydantic v2
- pydantic-settings
- SQLAlchemy 2.x sync style
- Alembic
- psycopg 3
- pytest
- Ruff
- Owns database access, external API access, AI integration, reports, chat logic, and secrets

Database:

- PostgreSQL
- Accessed only by backend
- Schema changes must use Alembic migrations

Infrastructure:

- Docker Compose runs frontend, backend, and PostgreSQL locally
- GitHub Actions handles basic CI checks
- No deployment automation in Phase 2

## Phase 2 Implementation Order

1. Review backend structure and commands.
2. Refine typed settings in `backend/app/core/config.py`.
3. Refine sync SQLAlchemy engine/session setup in `backend/app/core/database.py`.
4. Configure Alembic to use shared settings and model metadata.
5. Add initial SQLAlchemy models for planned v0 tables.
6. Generate and apply the first migration.
7. Add core error handling and basic logging.
8. Add backend tests for health/config/database behavior where useful.
9. Keep README and docs updated.

## Commands

Backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format .
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe change"
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
pnpm typecheck
pnpm build
```

Docker:

```bash
docker compose up --build
```

Git:

```bash
git status
git add .
git commit -m "Describe change"
git push
```

## Coding Rules

- Keep frontend API calls inside `frontend/lib/api/`.
- Do not call market data, news, LLM APIs, or the database directly from the frontend.
- Keep backend modules under `backend/app/modules/`.
- Use service/repository boundaries when business features are added later.
- Use sync SQLAlchemy for v0.
- Use Alembic for database schema changes.
- Do not commit real `.env` secrets.
- Do not commit generated caches such as `.venv`, `node_modules`, `.next`, or `*.tsbuildinfo`.
- Add focused tests for backend behavior.
- Run backend `pytest` and `ruff check` before committing backend changes.
- Run frontend `typecheck` and `build` before committing frontend changes.

## Existing Health Check

Backend endpoint:

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
