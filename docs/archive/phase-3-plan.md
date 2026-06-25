# Phase 3 Plan: Holdings and Watchlist Modules

## Summary

Phase 3 builds the first real product features on top of the Phase 2 foundation: manual CRUD for **Holdings** and **Watchlist** items, end to end (backend module layers + frontend pages).

The `Holding` and `WatchlistItem` ORM models already exist (`backend/app/models/`), so the database schema is done. Phase 3 adds the `router → service → repository` layers, Pydantic request/response schemas, backend tests, and the frontend pages that consume the new APIs. No market data, prices, or AI — just trustworthy manual data management that persists in PostgreSQL.

## In Scope

- Holdings module: `schemas.py`, `repository.py`, `service.py`, `router.py`.
- Watchlist module: same four files (same pattern).
- CRUD REST APIs for holdings and watchlist items (list, create, get one, update, delete).
- Pydantic request/response schemas with input validation (ticker, shares, average_cost).
- Service-layer rules: ticker normalization, not-found → `AppError(404)`.
- Backend tests: create, list, get, update, delete, validation failure (422), not-found (404).
- Register both routers in `app/main.py`.
- Frontend Holdings page and Watchlist page (forms + tables).
- Frontend API client functions under `frontend/lib/api/`.
- Loading, error, and empty states on both pages.
- Update `CLAUDE.md` (replace "only `health/` exists") once the modules land.

## Out of Scope

- Market data provider integration, current price, daily change.
- Real stock charts.
- News integration.
- AI action labels, AI reports, chat.
- Authentication, multi-user, deployment automation.
- New Alembic migration — **only** add one if a holdings/watchlist column actually changes.

## REST API Design

Resource-per-module, all under the existing `/api` prefix.

| Method | Path | Purpose | Success |
|--------|------|---------|---------|
| GET | `/api/holdings` | list all holdings | 200 |
| POST | `/api/holdings` | create | 201 |
| GET | `/api/holdings/{id}` | get one | 200 / 404 |
| PUT | `/api/holdings/{id}` | update (partial body) | 200 / 404 |
| DELETE | `/api/holdings/{id}` | delete | 204 / 404 |

Watchlist mirrors this exactly under `/api/watchlist`.

## Implementation Plan

Build Holdings as a full vertical slice first (it teaches the whole pattern), then repeat for Watchlist.

1. **Holdings — `schemas.py`** — `HoldingCreate`, `HoldingUpdate` (all fields optional), `HoldingRead` (`from_attributes=True`). Validation: `shares > 0`, `average_cost >= 0`, ticker length, ticker uppercased.
2. **Holdings — `repository.py`** — pure DB access taking a `Session`: `list_all`, `get`, `create`, `update`, `delete`. SQLAlchemy 2.x (`select()`, `session.get()`).
3. **Holdings — `service.py`** — business rules + orchestration: normalize input, raise `AppError("holding_not_found", ..., 404)` when missing, call the repository.
4. **Holdings — `router.py`** — FastAPI routes, `Depends(get_db)`, `response_model`, correct status codes.
5. **Wire up** — `include_router` in `app/main.py`.
6. **Holdings — tests** — `backend/tests/test_holdings.py` covering the matrix below.
7. **Watchlist** — repeat steps 1–6 (`reason_to_watch` instead of shares/cost; no numeric validation).
8. **Frontend** — API client functions, Holdings page, Watchlist page, with loading/error/empty states.
9. **Docs + checks** — update `CLAUDE.md`; run `ruff check`, `pytest`, `pnpm typecheck`, `pnpm build`.

## Decisions (resolved)

- **`target_allocation` units** — **fraction (`0`–`1`)**. Stored the same way actual allocation is computed (`position_value / portfolio_value`), so target and actual compare directly with no conversion. Schema constraint: `Field(ge=0, le=1)`.
- **Test database strategy** — **SQLite in-memory** with a `get_db` dependency override. Holdings/Watchlist use only `String`/`Text`/`Numeric`, so SQLite is faithful enough; keeps `pytest` infra-free in CI. Revisit (Postgres test DB) for Postgres-specific modules later (e.g. `market_data_cache` JSON).
- **Watchlist route** — `/api/watchlist`.

## Field Rules

- **Holdings** — required: `ticker`, `shares`, `average_cost`. Optional: `company_name`, `sector`, `notes`, `target_allocation`, `investment_thesis`.
- **Watchlist** — required: `ticker`. Optional: `company_name`, `sector`, `reason_to_watch`, `notes`.
- Tickers are stored uppercase, trimmed, `String(16)`.

## Test Matrix (per module)

- Create with valid body → 201, returns row with `id` + timestamps.
- List → 200, includes created rows.
- Get existing → 200; get missing → 404.
- Update existing → 200, fields changed; update missing → 404.
- Delete existing → 204; delete missing → 404.
- Invalid body (negative shares, missing ticker) → 422.

## Acceptance Criteria

Phase 3 is complete when:

- User can create, edit, and delete holdings through the API and the frontend.
- User can create, edit, and delete watchlist items the same way.
- Data persists in PostgreSQL across restarts.
- Frontend displays holdings and watchlist records with loading/error/empty states.
- Each module follows `router → service → repository` with Pydantic schemas.
- Backend CRUD tests pass; `ruff check` passes.
- Frontend `typecheck` and `build` pass.
- CI remains green.
- Phase 3 stays focused on manual management — no market data or AI features.
