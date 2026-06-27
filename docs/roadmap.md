# Roadmap & Progress

Single source of truth for project progress and the **current phase's** detailed scope. Always check the active phase here before writing code. High-level design lives in `docs/planning/`; implementation reference lives in `docs/guides/`.

## Current Status

- **Active Phase: Phase 4 — Market Data Integration**
- **Completed: Phase 0, Phase 1, Phase 2, Phase 3**

Phase 3 (Holdings/Watchlist CRUD) is complete and merged to `main` (PR #3). Phase 4 adds market data: a backend provider abstraction to fetch current price, daily change, and price history for holdings/watchlist tickers, cached to respect API rate limits, then surfaced as prices + basic charts in the frontend.

## Phase Overview

- [x] **Phase 0 — Planning and Design**
- [x] **Phase 1 — Repository and Development Environment Setup**
- [x] **Phase 2 — Backend and Database Foundation**
- [x] **Phase 3 — Holdings and Watchlist CRUD**
- [ ] **Phase 4 — Market Data Integration**  ← current
- [ ] **Phase 5 — News and Financial Data Integration**
- [ ] **Phase 6 — AI Report Generation**
- [ ] **Phase 7 — Chat Module**
- [ ] **Phase 8 — Export and Logging**
- [ ] **Phase 9 — UI Polish and Beginner Experience**
- [ ] **Phase 10 — Testing and Quality**
- [ ] **Phase 11 — README and Public Repo Documentation**
- [ ] **Phase 12 — Future Deployment Preparation**

## Phase 3 Detail (completed — merged in PR #3, 2026-06-25)

### Goal

Build manual Holdings and Watchlist management before adding market data, AI reports, or chat. The user should be able to create, view, update, and delete holdings and watchlist items through the backend API and frontend pages, with data persisted in PostgreSQL.

The `Holding` and `WatchlistItem` ORM models already exist in `backend/app/models/`, so **the schema is ready**: Phase 3 only adds the `router → service → repository` layers + Pydantic schemas + frontend pages. Do **not** "confirm schema" or create a new Alembic migration unless a holdings/watchlist field actually changes.

### In Scope

- Holdings module: `schemas.py`, `repository.py`, `service.py`, `router.py`.
- Watchlist module: same four files, same pattern.
- CRUD REST APIs for holdings and watchlist items (list, create, get one, update, delete).
- Pydantic request/response schemas with input validation (ticker, shares, average_cost).
- Service-layer rules: ticker normalization (trim + uppercase), not-found → `AppError(..., 404)`.
- Backend tests: create, list, get, update, delete, validation failure (422), not-found (404).
- Register both routers in `app/main.py`.
- Frontend Holdings page and Watchlist page (forms + tables).
- Frontend API client functions under `frontend/lib/api/`.
- Loading, error, and empty states on both pages.

### Out of Scope

- Market data provider integration, current price, daily change.
- Real stock charts.
- News integration.
- AI action labels, AI reports, chat.
- Import/export workflows.
- Authentication, multi-user, deployment automation.
- New Alembic migration — **only** add one if a holdings/watchlist column actually changes.

### REST API Design

Resource-per-module, all under the existing `/api` prefix. Partial updates use **`PATCH`** (not `PUT`).

| Method | Path | Purpose | Success |
|--------|------|---------|---------|
| GET | `/api/holdings` | list all holdings | 200 |
| POST | `/api/holdings` | create | 201 |
| GET | `/api/holdings/{id}` | get one | 200 / 404 |
| PATCH | `/api/holdings/{id}` | update (partial body) | 200 / 404 |
| DELETE | `/api/holdings/{id}` | delete | 204 / 404 |

Watchlist mirrors this exactly under `/api/watchlist` (`/api/watchlist/{id}` for get/patch/delete).

### Field Rules

- **Holdings** — required: `ticker`, `shares`, `average_cost`. Optional: `company_name`, `sector`, `notes`, `target_allocation`, `investment_thesis`.
- **Watchlist** — required: `ticker`. Optional: `company_name`, `sector`, `reason_to_watch`, `notes`.
- Tickers are stored uppercase, trimmed, `String(16)`.
- Validation: `shares > 0`, `average_cost >= 0`, ticker length within `String(16)`. Optional text fields may be empty or null.

### Implementation Steps

Build Holdings as a full vertical slice first (it teaches the whole pattern), then repeat for Watchlist.

1. **Holdings — `schemas.py`** — `HoldingCreate`, `HoldingUpdate` (all fields optional for PATCH), `HoldingRead` (`from_attributes=True`). Validation: `shares > 0`, `average_cost >= 0`, ticker length, ticker uppercased.
2. **Holdings — `repository.py`** — pure DB access taking a `Session`: `list_all`, `get`, `create`, `update`, `delete`. SQLAlchemy 2.x (`select()`, `session.get()`).
3. **Holdings — `service.py`** — business rules + orchestration: normalize input, raise `AppError("holding_not_found", ..., 404)` when missing, call the repository.
4. **Holdings — `router.py`** — FastAPI routes, `Depends(get_db)`, `response_model`, correct status codes (201 create, 200 read/update, 204 delete).
5. **Wire up** — `include_router` in `app/main.py`.
6. **Holdings — tests** — `backend/tests/test_holdings.py` covering the test matrix below.
7. **Watchlist** — repeat steps 1–6 (`reason_to_watch` instead of shares/cost; no numeric validation).
8. **Frontend** — API client functions, Holdings page, Watchlist page, with loading/error/empty states.
9. **Docs + checks** — update `docs/guides/` (`backend.md`, `database.md`, `api.md`); run `ruff check`, `pytest`, `pnpm typecheck`, `pnpm build`.

### Test Matrix (per module)

- Create with valid body → 201, returns row with `id` + timestamps.
- List → 200, includes created rows.
- Get existing → 200; get missing → 404.
- Update (PATCH) existing → 200, fields changed; update missing → 404.
- Delete existing → 204; delete missing → 404.
- Invalid body (negative shares, missing ticker) → 422.

### Resolved Decisions

- **`target_allocation` units** — **fraction (`0`–`1`)**. Stored the same way actual allocation is computed (`position_value / portfolio_value`), so target and actual compare directly with no conversion. Schema constraint: `Field(ge=0, le=1)`.
- **Test database strategy** — **SQLite in-memory** with a `get_db` dependency override. Holdings/Watchlist use only `String`/`Text`/`Numeric`, so SQLite is faithful enough and keeps `pytest` infra-free in CI. Revisit a Postgres test DB for Postgres-specific modules later (e.g. `market_data_cache` JSON).
- **Watchlist route** — `/api/watchlist`.

### Acceptance Criteria

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

## Current Phase Detail: Phase 4 — Market Data Integration

### Goal

Fetch and display real market data — current quote, daily change, historical price/volume — for holdings and watchlist tickers, behind a swappable `MarketDataProvider` abstraction, cached in the existing `market_data_cache` table to respect free-tier limits. Add a per-stock detail page with a price/volume chart, and surface market value + unrealized P/L on Holdings.

### Provider Decision

**yfinance** is the first concrete provider (no API key; Yahoo-sourced — accurate and complete for U.S. equities; the design doc's "prototype fallback"). Used for local development and **replaced with a keyed production API at deployment** — exactly the swap the abstraction exists for. Rationale vs alternatives: Finnhub's free tier no longer serves historical stock candles (charts would break); FMP's free tier caps ~250 req/day. yfinance has the fewest limits for the chart requirement and zero signup friction.

### In Scope

- New `market_data` backend module: `provider.py` (the `MarketDataProvider` interface), `providers/yfinance_provider.py` (concrete), `service.py` (cache-aware orchestration), `repository.py` (read/write `market_data_cache`), `router.py`, `schemas.py`.
- `MarketDataProvider` interface, Phase 4 subset: `get_quote(ticker)`, `get_price_history(ticker, range)`.
- Caching via the existing `market_data_cache` table: quotes short TTL (~2 min), history longer (~5 min intraday … ~1 day for 1y). Fresh hit returns the stored payload; miss/stale fetches + upserts.
- REST endpoints (see table); register the router in `app/main.py`.
- Frontend: `lib/api/market.ts` client; price + daily % change (green/red) on Holdings/Watchlist tables; **market value + unrealized gain/loss %** on Holdings (shares × price vs `average_cost`); a new `/stocks/[ticker]` detail page with a price/volume chart + range toggle (1D/1W/1M/1Y).
- Tests: provider **mocked** (no live calls in CI), service cache hit/miss + TTL, bad range → 422, unknown ticker → 404, P/L math.

### Out of Scope

- News, earnings/financial snapshots (Phase 5); AI reports/chat (Phase 6+).
- Index data (S&P 500 / Nasdaq) — deferred until the dashboard needs market context.
- Technical indicators, real-time streaming, options/crypto/forex.
- Swapping to a paid/official provider — that happens at deployment.

### REST API Design

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| GET | `/api/market/quote/{ticker}` | current quote (price, change, %change, prev close, high/low, volume) | 200 / 404 |
| GET | `/api/market/history/{ticker}?range=1d\|1w\|1m\|1y` | OHLCV series for charts | 200 / 404 / 422 |

A batch `GET /api/market/quotes?tickers=A,B,C` may be added in step 6 if the tables need it.

### Provider Abstraction & Caching

- `MarketDataProvider` is a `typing.Protocol` in `provider.py`; `service.py` depends on the Protocol, not yfinance, so a future `FinnhubProvider`/`FmpProvider` is a drop-in. Active provider chosen via config (`MARKET_DATA_PROVIDER`, default `yfinance`). Providers return normalized `schemas`, never raw API payloads.
- Cache key = `f"{provider}:{kind}:{ticker}:{range}"`. On read: `expires_at > now()` → return `payload`; else fetch → normalize → upsert with new `expires_at`. TTLs revisited after live testing.

### Implementation Steps

1. Add `yfinance` to backend deps; add `MARKET_DATA_PROVIDER` setting (default `yfinance`).
2. `provider.py` (`MarketDataProvider` Protocol) + `schemas.py` (`Quote`, `Candle`, `PriceHistory`).
3. `providers/yfinance_provider.py` — implement `get_quote` + `get_price_history`, normalize to schemas, unknown ticker → `AppError(404)`.
4. `repository.py` — cache read/upsert against `market_data_cache`.
5. `service.py` — cache-aware `get_quote`/`get_price_history` + range validation.
6. `router.py` — the two endpoints; register in `app/main.py`.
7. Backend tests with a mocked provider (cache hit/miss, TTL, 404, 422).
8. Frontend `lib/api/market.ts`; price + % change + P/L on Holdings/Watchlist; `/stocks/[ticker]` page + chart (range toggle). Chart lib chosen here (default: `recharts`; there is an existing `components/charts/StockPriceChart.tsx` stub to build on).
9. Docs + checks: update `docs/guides/api.md` (+ `backend.md`); `ruff`, `pytest`, `pnpm typecheck`, `pnpm build`; append `CHANGELOG.md`.

### Test Matrix

- `get_quote`: cache miss fetches + stores (200); cache hit returns stored payload without re-fetching; unknown ticker → 404.
- `get_price_history`: valid range → 200 series; bad range → 422; unknown ticker → 404; TTL respected.
- Holdings P/L: value = shares × price; gain/loss % vs `average_cost` correct (incl. zero-cost edge).

### Resolved Decisions

- **Provider:** yfinance first (swappable behind `MarketDataProvider`; replaced at deployment).
- **Chart placement:** new `/stocks/[ticker]` detail page.
- **Holdings P/L:** yes — market value + unrealized gain/loss on the Holdings table.
- **Indexes:** deferred out of Phase 4.

### Acceptance Criteria

- Holdings & Watchlist show current price + daily % change; Holdings also show market value + unrealized P/L.
- `/stocks/[ticker]` shows a price/volume chart with a working 1D/1W/1M/1Y toggle.
- Market data is cached in `market_data_cache`; repeated loads don't re-hit the provider within TTL.
- Provider sits behind `MarketDataProvider`; swapping providers needs no change to service/router.
- Backend tests pass with the provider mocked (no network in CI); `ruff` clean; frontend `typecheck` + `build` pass.
- No news/AI/index scope crept in.
