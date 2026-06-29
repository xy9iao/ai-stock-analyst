# API Guide

REST API exposed by the FastAPI backend. All routes are under `/api`. The
frontend reaches these only through `frontend/lib/api/` — never the DB directly.

Interactive docs are served at `/docs` (Swagger) and `/redoc` when the backend runs.

## Conventions

- **Resource per module**, one router each (`health`, `holdings`, `watchlist`).
- **Partial updates use `PATCH`** (not `PUT`) — the body contains only the fields to change.
- **Status codes:** `200` read/update, `201` create, `204` delete, `404` not found, `422` validation error.
- **Tickers** are normalized server-side: trimmed and uppercased before storage.
- **Money/quantity fields** (`shares`, `average_cost`, `target_allocation`) are JSON
  **strings**, not numbers — the backend serializes `Decimal` as a string to preserve precision.

## Error shape

Handled errors (e.g. a missing row) return a stable body:

```json
{ "detail": { "code": "holding_not_found", "message": "Holding with id 5 not found" } }
```

Request-validation errors (FastAPI/Pydantic) return `422` with a list-shaped `detail`.

## Health

| Method | Path | Success |
|--------|------|---------|
| GET | `/api/health` | `200` `{ "status": "ok", "service": "ai-stock-analyst-backend" }` |

## Holdings

Stocks the user owns.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| GET | `/api/holdings` | list all | `200` |
| POST | `/api/holdings` | create | `201` / `422` |
| GET | `/api/holdings/{id}` | get one | `200` / `404` |
| PATCH | `/api/holdings/{id}` | partial update | `200` / `404` / `422` |
| DELETE | `/api/holdings/{id}` | delete | `204` / `404` |

**Fields** — required: `ticker`, `shares`, `average_cost`. Optional: `company_name`,
`sector`, `notes`, `target_allocation`, `investment_thesis`.

**Validation** — `shares > 0`, `average_cost >= 0`, `0 <= target_allocation <= 1`
(stored as a fraction), `ticker` length ≤ 16.

```jsonc
// POST /api/holdings
{ "ticker": "nvda", "shares": "3", "average_cost": "850.50", "sector": "Semiconductors" }
// 201 ->
{ "id": 1, "ticker": "NVDA", "shares": "3", "average_cost": "850.50",
  "company_name": null, "sector": "Semiconductors", "notes": null,
  "target_allocation": null, "investment_thesis": null,
  "created_at": "…", "updated_at": "…" }
```

## Watchlist

Stocks the user is tracking but may not own. Same shape as holdings under `/api/watchlist`.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| GET | `/api/watchlist` | list all | `200` |
| POST | `/api/watchlist` | create | `201` / `422` |
| GET | `/api/watchlist/{id}` | get one | `200` / `404` |
| PATCH | `/api/watchlist/{id}` | partial update | `200` / `404` / `422` |
| DELETE | `/api/watchlist/{id}` | delete | `204` / `404` |

**Fields** — required: `ticker`. Optional: `company_name`, `sector`, `reason_to_watch`, `notes`.
No numeric fields, so the only validation failure is a missing/oversized `ticker`.

## Market data

Live quotes and price history, fetched via a swappable provider (default: **yfinance**,
no API key) and cached in the `market_data_cache` table (quote TTL ~2 min, history
longer by range). Numeric fields are JSON **strings** (Decimal). Unknown ticker → `404`.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| GET | `/api/market/quote/{ticker}` | current quote | `200` / `404` |
| GET | `/api/market/history/{ticker}?range=1d\|1w\|1m\|1y` | OHLCV history (default `1d`) | `200` / `404` / `422` |

**Quote** — `ticker`, `price`, `change`, `change_percent`, `previous_close`, plus optional
`open`, `day_high`, `day_low`, `volume`, `as_of`.

**PriceHistory** — `ticker`, `range`, and `candles[]` (each: `timestamp`, `open`, `high`,
`low`, `close`, `volume`).

```jsonc
// GET /api/market/quote/NVDA  -> 200
{ "ticker": "NVDA", "price": "192.5300", "change": "-2.2700",
  "change_percent": "-1.1653", "previous_close": "194.8000",
  "open": "194.0000", "day_high": "195.1000", "day_low": "191.5000",
  "volume": 178906300, "as_of": "…" }
```
