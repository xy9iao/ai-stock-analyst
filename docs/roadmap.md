# Roadmap & Progress

Single source of truth for project progress and the active phase's scope. Check here before writing code. Design intent lives in `docs/planning/`; implementation reference in `docs/guides/`; the accurate build history in `CHANGELOG.md`.

## Current Status

- **v0 is complete — all 12 phases done** (2026-06 → 2026-07-03). The demo-hardening code is built and tested; going live = following `docs/guides/deployment.md` (Vercel + Render + Neon accounts), then pasting the URL into the README.
- **Next:** the **next version (agent-focused)**, planned first in `docs/planning/`. Deferred ideas stay as GitHub issues.

## v0 Phase Summary

| Phase | Delivered | Merged |
|---|---|---|
| 0 — Planning & design | charter, vision, requirements, user stories, architecture, data sources, AI design (`docs/planning/`) | pre-repo |
| 1 — Repo & dev environment | monorepo, backend/frontend skeletons, Docker Compose, CI pipeline | direct to `main` |
| 2 — Backend & DB foundation | typed settings, SQLAlchemy 2 + Alembic + psycopg 3, all 8 tables in one initial migration, `AppError` + logging, test scaffold | [PR #1](https://github.com/xy9iao/ai-stock-analyst/pull/1) |
| 3 — Holdings & watchlist CRUD | both modules (router→service→repository+schemas), REST CRUD, validation, first frontend pages + typed API client | [PR #3](https://github.com/xy9iao/ai-stock-analyst/pull/3) |
| 4 — Market data | `MarketDataProvider` Protocol + yfinance impl, Postgres cache-aside, quote/history APIs, charts + live prices in UI | [PR #5](https://github.com/xy9iao/ai-stock-analyst/pull/5) |
| 5 — News & financials | news + financials modules on the same provider/cache pattern (backend-only; feeds AI context) | [PR #6](https://github.com/xy9iao/ai-stock-analyst/pull/6) |
| 6 — AI reports | `ai/` module: single LLM gateway (`llm_client`), compact DB-context injection, prompt safety boundary, reports stored as Markdown | [PR #7](https://github.com/xy9iao/ai-stock-analyst/pull/7) |
| 7 — Chat | multi-turn investment chat with **toggleable context** (holdings/watchlist/ticker/reports), history capped, same LLM gateway | [PR #8](https://github.com/xy9iao/ai-stock-analyst/pull/8) |
| 8 — Export | client-side Markdown download for reports + chat (logging idea deferred) | [PR #12](https://github.com/xy9iao/ai-stock-analyst/pull/12) |
| 9 — UI polish | top-nav app shell, design system (Button/Card/Input/Badge + tokens), four-state views, toasts, tooltips, disclaimer footer, responsive nav, minimal Home | [PR #13](https://github.com/xy9iao/ai-stock-analyst/pull/13) |
| 10 — Testing | frontend Vitest + RTL suite (28 tests) wired into CI; backend `pytest-cov` (43 tests, coverage measured not gated) | [PR #17](https://github.com/xy9iao/ai-stock-analyst/pull/17) |
| 11 — README | big-company-OSS-style README: badges, screenshots, Mermaid architecture, getting started | [PR #18](https://github.com/xy9iao/ai-stock-analyst/pull/18) |
| 12 — Deployment | anonymous session isolation, three-layer LLM cost defense (prepaid cap / master switch / per-session caps), `llm_calls` + `/api/stats` observability, Vercel+Render+Neon deploy guide | PR #20 |

**Off-roadmap work:** MIT license ([#4](https://github.com/xy9iao/ai-stock-analyst/pull/4)) · frontend MVP UI for reports/chat ([#9](https://github.com/xy9iao/ai-stock-analyst/pull/9)) · one-command Docker dev ([#10](https://github.com/xy9iao/ai-stock-analyst/pull/10)) · ESLint 9 flat config + lint CI gate ([#11](https://github.com/xy9iao/ai-stock-analyst/pull/11), closed issue #2) · v0 docs freeze (this branch).

## Phase 12 — Deployment (completed)

Delivered exactly the approved scope — a demo-hardened deployment with 2–3 defensible production decisions, no K8s/Terraform/staging/auth/monitoring-stack/load-testing:

1. **Anonymous session isolation** behind `DEMO_MODE` (default off — local behavior unchanged; pre-demo rows backfilled to the permanent `local` bucket): cookie middleware, `session_id` buckets on holdings/watchlist/reports/chat, 7-day TTL cleanup, a "New demo session" footer button.
2. **Three-layer cost defense:** ① DeepSeek prepaid = budget hard cap · ② LLM master switch (`settings.llm_enabled_until`, admin-token endpoint, checked at the `llm_client` gateway, default OFF, TTL-bound enable) · ③ per-session caps counted in **LLM calls** (reports ≤3, chat ≤20, `429`).
3. **Observability:** `llm_calls` table (tokens/latency; `route`/`steps` reserved for the agent version) + structured logs + `GET /api/stats`.
4. One reviewed migration (`b3074aa5c807`). 52 backend tests (9 new).
5. **Deploy guide** (`docs/guides/deployment.md`): Vercel + Render free + Neon free; cold start accepted with an application-season upgrade TODO; CI gates the merge, the merge is the deploy (platform auto-deploy on `main`).

## Backlog (deferred to issues)

- [#14](https://github.com/xy9iao/ai-stock-analyst/issues/14) — Home page: news + financials for tracked tickers
- [#15](https://github.com/xy9iao/ai-stock-analyst/issues/15) — ticker autocomplete (needs a symbol-search provider)
- [#16](https://github.com/xy9iao/ai-stock-analyst/issues/16) — Playwright E2E for critical flows

## Post-v0 Direction

**Agent-based research workflows** — multi-step analysis, automated news digging, RAG over reports/notes — deliberately kept out of v0 (`planning/ai-design.md`). The next version starts with a fresh planning pass in `docs/planning/`.

---

*Detailed per-phase scope/decision records for completed phases live in `CHANGELOG.md` — this file stays lean and forward-looking.*
