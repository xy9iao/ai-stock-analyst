# Roadmap & Progress

Single source of truth for project progress and the **current phase's** detailed scope. Always check the active phase here before writing code. High-level design lives in `docs/planning/`; implementation reference lives in `docs/guides/`.

## Current Status

- **Next: Phase 10 — Testing & Quality.**
- **Completed: Phase 0 – Phase 9**, plus the MVP frontend, one-command Docker dev (PR #10), and the lint fix (PR #11, closed #2).

The **MVP is done and polished**: holdings/watchlist, market data, news/financials, AI reports, and chat — one cohesive app (shared top-nav shell, a documented design system in `docs/guides/frontend.md`, loading/empty/error states, beginner tooltips + a disclaimer footer, responsive), with `docker compose up --build` running the whole stack. Remaining phases are testing/infra.

## Phase Overview

- [x] **Phase 0 — Planning and Design**
- [x] **Phase 1 — Repository and Development Environment Setup**
- [x] **Phase 2 — Backend and Database Foundation**
- [x] **Phase 3 — Holdings and Watchlist CRUD**
- [x] **Phase 4 — Market Data Integration**
- [x] **Phase 5 — News and Financial Data Integration**
- [x] **Phase 6 — AI Report Generation**
- [x] **Phase 7 — Chat Module**
- [x] **Phase 8 — Export** (logging deferred)
- [x] **Phase 9 — UI Polish and Beginner Experience**
- [ ] **Phase 10 — Testing and Quality**  ← next
- [ ] **Phase 11 — README and Public Repo Documentation**
- [ ] **Phase 12 — Future Deployment Preparation**

## Phase 9 Detail (completed)

### Goal

Turn the six functional-but-plain pages into one cohesive, beginner-friendly app: a shared **top-nav shell**, a refined (still clean/minimal) **slate/emerald design system** captured in `docs/guides/frontend.md`, real **loading/empty/error states**, and plain-language **help for finance terms**. **Frontend-only** — no backend, model, or migration changes.

### Decisions (agreed with the developer)

- **Top nav bar** (shared app shell) — not a sidebar.
- **Clean & minimal** — refine the existing slate/emerald, not a redesign.
- **Medium scope** — shell + design system + states + beginner UX.
- **New doc `docs/guides/frontend.md`** — the frontend implementation + design-system reference (tokens, shared components, UX patterns), written as we build. Fills the current gap (no frontend guide exists).
- Dark mode: **deferred** (optional).

### In Scope (reviewable steps)

1. **App shell + top nav** — `<TopNav>` (brand + page links, active highlight) wired into `app/layout.tsx`.
2. **Design tokens + shared components** — named color/spacing/radius/shadow tokens; consolidate repeated inline styles into `Button` (variants), `Card`, `Input`, `Badge`.
3. **States** — loading skeletons, friendlier empty states, toast for errors (replacing inline red boxes).
4. **Beginner experience** — `Tooltip` for finance terms (avg cost, day %, gain/loss), a persistent subtle "research, not financial advice" disclaimer, first-run empty-state guidance.
5. **Responsive pass** — collapsing nav, scroll/stack tables, stacked forms; verified at mobile width.
6. **Docs** — `docs/guides/frontend.md`, roadmap + CHANGELOG.

### Out of Scope

- Backend/API/model/migration changes.
- Dark mode (deferred), animations beyond basic transitions, new pages/features.
- Chart/data behavior changes — Phase 9 is presentation only.

### Verify

- `pnpm typecheck` + `pnpm lint` + `pnpm build` clean at each step.
- Manual: nav works across every page with correct active state; loading/empty/error states render; tooltips + disclaimer present; usable at phone width.

## Phase 8 Detail (completed — merged in PR #12)

### Goal

Let the user save AI **reports** and **chat conversations** as Markdown files (Obsidian-friendly), fulfilling the roadmap's "export button." Reports are already stored as Markdown and delivered to the frontend, so export is a pure client-side browser download — **no backend endpoint, no new model/migration.**

### In Scope

- `frontend/lib/download.ts` — `downloadText(filename, text)` (Blob → anchor download) + `slugFilename(title)`.
- Reports page: a **Download .md** button on the open report → saves `content_markdown` as `<title-slug>.md`.
- Chat page: an **Export** button (disabled when empty) → renders the conversation to Markdown (`**You:** / **Assistant:**`) → `chat.md`.

### Out of Scope

- Backend export endpoints — unnecessary; the data is already Markdown on the client.
- The "daily log / logging" idea — **deferred** (underspecified, low MVP value).
- PDF/other formats, bulk export, server-side file storage.

### Verify

- `pnpm typecheck` + `pnpm lint` + `pnpm build` all clean.
- Manually: open a report → **Download .md** saves it; send a chat message → **Export** saves the transcript.

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

## Phase 4 Detail (completed — merged in PR #5, 2026-06-29)

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

## Phase 5 Detail (completed — merged in PR #6, 2026-06-30)

### Goal

Fetch **company news** and a **latest financial/earnings snapshot** per holdings/watchlist ticker, behind provider interfaces (mirroring Phase 4's `MarketDataProvider`), cached in `market_data_cache`, and shaped into **compact** form — headlines/metadata + a snapshot, never full articles or full statements. Backend-only; this prepares the data the Phase 6 AI will consume.

### Provider Decision

**yfinance** supplies both news and financials — no new dependency, no API key (consistent with Phase 4; swapped at deployment). It exposes `.news` (Yahoo headlines) and `.info` / statements / `.calendar` (revenue, EPS, margins, earnings dates). News is a **secondary signal**: yfinance's feed is thinner/less reliable than its prices, which is acceptable since news is not core to the product.

### In Scope

- Two backend modules, each the standard `provider → service → repository → router` + `schemas`:
  - `news/` — `NewsProvider` Protocol, `providers/yfinance_news_provider.py`, cache-aside service, repository (reuse `market_data_cache`), router.
  - `financials/` — `FinancialDataProvider` Protocol, `providers/yfinance_financials_provider.py`, service, repository, router.
- Compact shapes:
  - `NewsItem`: `headline`, `source`, `published_at`, `summary?`, `url?`, `ticker`.
  - `FinancialSnapshot`: `ticker`, optional `revenue`, `revenue_growth`, `eps`, `net_income`, `gross_margin`, `operating_margin`, `last_earnings_date`, `next_earnings_date`, plus basic profile (`company_name`, `sector`, `industry`, `market_cap`).
- Endpoints: `GET /api/news/{ticker}` (recent items, capped) and `GET /api/financials/{ticker}`.
- Caching via `market_data_cache`: news medium TTL (~15 min), financials long TTL (~1 day).
- Token discipline: cap news items, trim summaries, snapshot fields only.
- Tests: providers mocked (no network in CI), cache hit/miss, unknown ticker → 404, news cap.

### Out of Scope

- Macro/market news (yfinance is weak at it — revisit with a news-grade provider).
- LLM context-package assembly and any AI calls (Phase 6).
- Frontend display of news/financials (later, with the AI/report UI).
- New Alembic migration (reuse `market_data_cache`).

### REST API Design

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| GET | `/api/news/{ticker}` | recent company news (compact) | 200 / 404 |
| GET | `/api/financials/{ticker}` | latest financial snapshot + profile | 200 / 404 |

### Implementation Steps

1. `news/` schemas + `NewsProvider` Protocol.
2. `news/providers/yfinance_news_provider.py` — map `yf.Ticker(t).news` → `NewsItem[]`, cap + trim, unknown ticker → 404.
3. `news/` repository + cache-aside service + router; register in `main.py`.
4. `financials/` schemas + `FinancialDataProvider` Protocol.
5. `financials/providers/yfinance_financials_provider.py` — map yfinance `.info`/statements/`.calendar` → `FinancialSnapshot`.
6. `financials/` repository + service + router; register in `main.py`.
7. Tests (`test_news.py`, `test_financials.py`) with mocked providers.
8. Docs + checks: update `docs/guides/api.md` (+ `backend.md`); `ruff`, `pytest`; append `CHANGELOG.md`.

### Resolved Decisions

- **Provider:** yfinance for both news and financials (no new dependency, no key; swap at deployment).
- **Scope:** backend-only (no frontend this phase).
- **Macro news:** deferred (yfinance limitation).
- **Cache:** reuse `market_data_cache`; no new migration.

### Acceptance Criteria

- `GET /api/news/{ticker}` returns recent compact news items; unknown ticker → 404.
- `GET /api/financials/{ticker}` returns a compact snapshot + basic profile; unknown ticker → 404.
- Both cached in `market_data_cache`; repeats don't re-hit yfinance within TTL.
- Providers sit behind their interfaces; tests pass with providers mocked (no network in CI); `ruff` clean.
- No AI, frontend, or macro-news scope crept in.

## Phase 6 Detail (completed — merged in PR #7, 2026-06-30)

### Goal

Generate AI investment reports — **single-stock** and **portfolio** — behind one centralized `ai/` module. Load DB rows (holdings/watchlist) + cached market/news/financials into a **compact** context, call DeepSeek (OpenAI-compatible), store the Markdown in the `reports` table, return it. Backend-only this phase.

### LLM Decision

**DeepSeek** (cloud, OpenAI-compatible) via the existing `LLM_*` config. `.env`: `LLM_BASE_URL=https://api.deepseek.com`, `LLM_API_KEY=<key>`, `LLM_MODEL=deepseek-chat`. The client uses the `openai` SDK pointed at `LLM_BASE_URL`. Tests **mock** the client (no live calls / cost / key needed in CI); a real key is only needed for live verification.

### In Scope

- New `ai/` module — **the only place LLM calls happen**:
  - `llm_client.py` — thin OpenAI-compatible chat wrapper (`complete(system, user) -> str`); LLM/network errors → `AppError(502)`.
  - `context.py` — assemble the **compact context** (loads holdings/watchlist repos + market/news/financials services into compact shapes).
  - `prompt_builder.py` — system prompt (conclusion-first style, action labels, confidence, long-term/swing views, beginner-friendly, **financial-advice safety boundary**) + user prompt per report type.
  - `report_generator.py` — orchestrate build → call → store → return.
  - `repository.py` — `reports` table read/write (create, list, get).
  - `schemas.py`, `router.py`.
- Add the `openai` dependency.
- Report types: **single_stock** (input: ticker) and **portfolio** (uses all holdings).
- Persist to the existing `reports` table (`report_type`, `title`, `content_markdown`).

### Out of Scope

- Chat (Phase 7); watchlist + market-overview report types (later — same pipeline); RAG/agents; streaming.
- Frontend report UI (later UI phase) — view via `/docs` / curl for now.
- New Alembic migration (the `reports` table exists from Phase 2).

### REST API Design

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| POST | `/api/reports` | generate a report (`single_stock` or `portfolio`) | `201` / `422` / `404` / `502` |
| GET | `/api/reports` | list recent reports | `200` |
| GET | `/api/reports/{id}` | get one report | `200` / `404` |

`POST` body: `{ "report_type": "single_stock" | "portfolio", "ticker"?: str }` (ticker required for `single_stock`).

### Compact Context (token discipline)

- **single_stock:** the holding/watchlist row if present + latest quote + a few news headlines + the financial snapshot — compact shapes, capped.
- **portfolio:** all holdings with quote + unrealized P/L + a short market summary + top headlines — capped (limit holdings/news items).
- Never send raw API payloads, full articles, or full statements (`planning/ai-design.md` §16–18).

### Report Style (from `planning/ai-design.md`)

Conclusion-first; suggested action (Strong Buy … Avoid) with reasoning; separate long-term vs swing view; confidence (Low/Med/High); beginner-friendly; risks when meaningful; safety boundary (no "guaranteed profit", "this is not financial advice"). Markdown output.

### Implementation Steps

1. Add `openai` dep; document `.env` (`LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL`).
2. `ai/llm_client.py` — the single LLM call site (OpenAI-compatible chat completion).
3. `ai/schemas.py` — `ReportRequest` (report_type enum, optional ticker), `ReportRead`.
4. `ai/context.py` — compact context assembly for single-stock + portfolio.
5. `ai/prompt_builder.py` — system prompt (style + safety boundary) + per-type user prompt.
6. `ai/report_generator.py` + `ai/repository.py` — orchestrate, persist to `reports`.
7. `ai/router.py` — endpoints; register in `main.py`.
8. Tests with `llm_client` mocked (no network/cost).
9. Docs + checks: `docs/guides/api.md` (+ `backend.md`, `.env.example`); `ruff`, `pytest`; append `CHANGELOG.md`.

### Resolved Decisions

- **LLM:** DeepSeek (cloud, OpenAI-compatible; key in `.env`); `openai` SDK client.
- **Report types:** single-stock + portfolio (watchlist/market-overview later).
- **Scope:** backend-only.
- **Persistence:** existing `reports` table (no migration).
- **Tests:** mock the LLM client — no live calls, cost, or key in CI.

### Acceptance Criteria

- `POST /api/reports` (single_stock + ticker) → `201`, a Markdown report stored in `reports` and returned.
- `POST /api/reports` (portfolio) → `201`, a portfolio Markdown report.
- `GET /api/reports` lists; `GET /api/reports/{id}` fetches; missing → `404`; bad body → `422`.
- **Every** LLM call goes through `ai/llm_client.py`; context is compact (no raw payloads); the safety boundary is in the system prompt.
- Tests pass with the LLM mocked; `ruff` clean.
- No chat, frontend, or extra report types crept in.

## Phase 7 Detail (completed — merged in PR #8, 2026-06-30)

### Goal

An investment-focused chat assistant. Multi-turn chat with **modular, toggleable context injection** — each message declares which DB context to include (holdings, watchlist, a specific ticker, recent reports), and the service injects only what's enabled. Reuses the centralized `ai/llm_client`; stores history in the existing `chat_sessions`/`chat_messages` tables. Backend-only.

### Decisions (resolved)

- **Context injection:** modular/toggleable — the request carries flags (`include_holdings`, `include_watchlist`, `ticker`, `include_recent_reports`). Designed so the future chat UI is just toggle buttons over these.
- **Scope:** backend-only (chat UI lands in the UI-polish phase).
- **Non-streaming** (return the full reply); RAG/agents deferred.

### In Scope

- New `chat/` module: `schemas`, `repository` (sessions + messages CRUD), `service` (orchestration + scope control), `router`.
- Extend `ai/llm_client` with a multi-turn `chat(messages) -> str` — still **the single LLM call site**.
- `ChatContextOptions` toggles → the service assembles a compact context block from the enabled sources, reusing `ai/context` (holdings via portfolio context; a ticker via single-stock context) + small helpers (watchlist list, recent report titles).
- Investment-only **scope control** in the system prompt (redirect off-topic questions).
- Persist user + assistant messages (role + content) per session.

### Out of Scope

- Streaming responses; RAG/agents; frontend (UI phase).
- New Alembic migration (`chat_sessions`/`chat_messages` exist from Phase 2).
- Heavy per-message context beyond the four toggles (keep it compact).

### REST API Design

| Method | Path | Purpose | Success / Errors |
|--------|------|---------|------------------|
| POST | `/api/chat/messages` | send a message, get a reply (creates a session if none given) | `201` / `404` / `422` / `502` |
| GET | `/api/chat/sessions` | list chat sessions | `200` |
| GET | `/api/chat/sessions/{id}/messages` | a session's messages | `200` / `404` |

`POST` body: `{ "session_id"?: int, "message": str, "context"?: { "include_holdings"?: bool, "include_watchlist"?: bool, "ticker"?: str, "include_recent_reports"?: bool } }` → returns `{ session_id, reply }`.

### Implementation Steps

1. Extend `ai/llm_client` with `chat(messages: list[dict]) -> str` (multi-turn; still the only call site).
2. `chat/schemas.py` — `ChatContextOptions`, `ChatMessageRequest`, `ChatMessageRead`, `ChatSessionRead`.
3. `chat/repository.py` — create session, append message, list sessions, get a session's messages.
4. `chat/context.py` — assemble the compact context block from the enabled toggles (reuse `ai/context`).
5. `chat/service.py` — orchestrate: load/create session + history → build context → build messages (system + context + history + user) → `llm_client.chat` → store user + assistant → return.
6. `chat/router.py` — endpoints; register in `main.py`.
7. Tests with `llm_client` + context mocked (no network/cost).
8. Docs + checks: `docs/guides/api.md` (+ `backend.md`); `ruff`, `pytest`; append `CHANGELOG.md`.

### Test Matrix

- POST with no `session_id` → `201`, creates a session, returns `reply` + `session_id`.
- POST with an existing `session_id` → continues; the session's message history grows (user + assistant stored).
- Context toggles: `include_holdings` / `ticker` cause the corresponding context builder to be invoked (mocked).
- `GET /api/chat/sessions` lists; `GET …/{id}/messages` returns the conversation; unknown session → `404`.

### Acceptance Criteria

- A user can send chat messages and get investment-focused replies; history persists across a session.
- Context injection is toggleable per request (holdings / watchlist / ticker / recent reports).
- **Every** LLM call goes through `ai/llm_client`.
- Tests pass with the LLM mocked; `ruff` clean.
- No streaming, frontend, or out-of-scope context crept in.
