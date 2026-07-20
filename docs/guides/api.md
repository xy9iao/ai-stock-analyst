# API Guide

REST API exposed by the FastAPI backend. All routes are under `/api`. The
frontend reaches these only through `frontend/lib/api/` — never the DB directly.

Interactive docs are served at `/docs` (Swagger) and `/redoc` when the backend runs.

**Demo mode** (`DEMO_MODE=true`, public deployments only): every visitor gets an anonymous
`session_id` cookie and all user data (holdings, watchlist, reports, chat) is scoped to it —
another session's rows behave as `404`. LLM endpoints add two protections: a **master switch**
(off ⇒ `503` `llm_disabled`) and **per-session caps** (exceeded ⇒ `429` `demo_report_limit` /
`demo_chat_limit`). Locally (default) none of this is active and data lives in one shared bucket.

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

## News

Recent **company news** (compact metadata — headlines, not article bodies), via yfinance
(no key), cached ~15 min. Unlike the others, an **unknown ticker returns `200` with empty
`items`** — yfinance can't distinguish "no recent news" from "bad ticker".

| Method | Path | Purpose | Success |
|--------|------|---------|---------|
| GET | `/api/news/{ticker}` | recent company news (capped) | `200` |

**CompanyNews** — `ticker`, `items[]` (each: `headline`, `source?`, `published_at?`, `summary?`, `url?`).

## Financials

A compact **financial snapshot** + basic profile, via yfinance (no key), cached ~1 day.
Numeric fields are JSON **strings** (Decimal). Unknown ticker → `404`.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| GET | `/api/financials/{ticker}` | latest snapshot + profile | `200` / `404` |

**FinancialSnapshot** — `ticker`, plus optional `company_name`, `sector`, `industry`,
`market_cap`, `revenue`, `revenue_growth`, `eps`, `net_income`, `gross_margin`,
`operating_margin`, `last_earnings_date`, `next_earnings_date`.

## Reports (AI)

AI-generated investment reports (Markdown, stored in the `reports` table). The backend
loads a **compact** context (holdings/watchlist + cached market/news/financials) and calls
an OpenAI-compatible LLM (DeepSeek, configured by `LLM_*`). **Every** LLM call routes through
`app/modules/ai/llm_client.py`.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| POST | `/api/reports` | generate a report | `201` / `422` / `404` / `502` |
| GET | `/api/reports` | list recent reports | `200` |
| GET | `/api/reports/{id}` | get one report | `200` / `404` |

`POST` body: `{ "report_type": "single_stock" | "portfolio" | "research", "ticker"?: str, "query"?: str }` — `ticker` is
required for `single_stock`, `query` (≤500 chars) for `research` (else `422`); unknown ticker → `404`;
missing key → `503`; LLM error → `502`. `research` runs the Phase 13 agent loop (~10–40s) and
archives the memo like any other report (title = truncated query); demo mode counts it against
the same per-session report cap (`429` when exhausted).

**ReportRead** — `id`, `report_type`, `title`, `content_markdown`, `created_at`.

## Chat

An investment-focused chat assistant (multi-turn, backend-only). Routes through the
centralized `ai/llm_client`; stores history in `chat_sessions`/`chat_messages`. Context
injection is **toggleable per message**.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| POST | `/api/chat/messages` | send a message, get a reply | `201` / `404` / `422` / `502` |
| GET | `/api/chat/sessions` | list chat sessions | `200` |
| GET | `/api/chat/sessions/{id}/messages` | a session's messages | `200` / `404` |

`POST` body: `{ "message": str, "session_id"?: int, "context"?: { "include_holdings"?: bool,
"include_watchlist"?: bool, "ticker"?: str, "include_recent_reports"?: bool } }` — omit
`session_id` to start a new conversation. Returns `{ session_id, reply }`.

## Session (demo)

| Method | Path | Purpose | Success |
|--------|------|---------|---------|
| POST | `/api/session/reset` | drop the demo cookie; next request gets a fresh empty bucket | `204` |

## Admin & Stats

The admin endpoints require the `X-Admin-Token` header matching `ADMIN_TOKEN` (unset ⇒ always
`403`, fail-closed). `/api/stats` is public — aggregates only, no user data.

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| POST | `/api/admin/llm` | set the LLM master switch (`{ enabled, ttl_minutes? }`; on always expires after the TTL, default 60 min) | `200` / `403` |
| GET | `/api/admin/llm` | current switch state | `200` / `403` |
| GET | `/api/stats` | LLM usage aggregates (calls, prompt/completion/cached tokens, avg latency, by kind) from `llm_calls` | `200` |
