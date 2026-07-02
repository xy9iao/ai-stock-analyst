# Roadmap & Progress

Single source of truth for project progress and the active phase's scope. Check here before writing code. Design intent lives in `docs/planning/`; implementation reference in `docs/guides/`; the accurate build history in `CHANGELOG.md`.

## Current Status

- **v0 (MVP) is complete and feature-frozen** — Phases 0–11 merged (2026-06 → 2026-07-02).
- **Next: Phase 12 — Deployment Preparation**, the final v0 phase. Plan it before building (see below).
- No new core features land in v0. Deferred ideas are GitHub issues; the **next version (agent-focused)** will be planned in `docs/planning/`.

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

**Off-roadmap work:** MIT license ([#4](https://github.com/xy9iao/ai-stock-analyst/pull/4)) · frontend MVP UI for reports/chat ([#9](https://github.com/xy9iao/ai-stock-analyst/pull/9)) · one-command Docker dev ([#10](https://github.com/xy9iao/ai-stock-analyst/pull/10)) · ESLint 9 flat config + lint CI gate ([#11](https://github.com/xy9iao/ai-stock-analyst/pull/11), closed issue #2) · v0 docs freeze (this branch).

## Phase 12 — Deployment Preparation (next, not started)

Rough scope, to be planned in detail first: production configuration hardening (settings split, CORS, secrets story — `open-questions.md` Q25/Q26), hosting decision (frontend host + backend host + managed Postgres), production Docker images, deployment documentation. Goal: the repo is *ready* to deploy, not necessarily deployed.

## Backlog (deferred to issues)

- [#14](https://github.com/xy9iao/ai-stock-analyst/issues/14) — Home page: news + financials for tracked tickers
- [#15](https://github.com/xy9iao/ai-stock-analyst/issues/15) — ticker autocomplete (needs a symbol-search provider)
- [#16](https://github.com/xy9iao/ai-stock-analyst/issues/16) — Playwright E2E for critical flows

## Post-v0 Direction

**Agent-based research workflows** — multi-step analysis, automated news digging, RAG over reports/notes — deliberately kept out of v0 (`planning/ai-design.md`). The next version starts with a fresh planning pass in `docs/planning/`.

---

*Detailed per-phase scope/decision records for completed phases live in `CHANGELOG.md` — this file stays lean and forward-looking.*
