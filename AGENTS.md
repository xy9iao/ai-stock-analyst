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

Phase 1 is repository and development environment setup only.

Do not implement Holdings, Watchlist, market data, news, AI reports, chat, authentication, deployment automation, or production infrastructure unless the user explicitly starts a later phase.

## Architecture Boundaries

Frontend:

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui-style local components
- lucide-react
- Calls backend APIs only through `frontend/lib/api/`

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

Database:

- PostgreSQL
- Accessed only by backend
- Schema changes must use Alembic migrations

Infrastructure:

- Docker Compose runs frontend, backend, and PostgreSQL locally
- GitHub Actions handles basic CI checks

## Commands

Backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format .
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
