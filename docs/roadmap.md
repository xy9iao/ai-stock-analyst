# Roadmap & Progress

Single source of truth for project progress and the active phase's scope. Check here before writing code. Design intent lives in `docs/planning/`; implementation reference in `docs/guides/`; the accurate build history in `CHANGELOG.md`.

## Current Status

- **v0 shipped and frozen** — all 12 phases done, released as `v0.1.0`, live at https://ai-stock-analyst-pi.vercel.app. Bug fixes only.
- **Active version: v1 — Agent Layer (Phases 13–15), planned below.** Next up: **Phase 13** (not started — produce a plan for review before any code, per phase discipline).
- Anything not listed in the v1 plan is **out of scope by default**; deferred ideas stay as GitHub issues.

## v1 — Agent Layer, MCP, RAG, Context & Injection Defense (Phases 13–15)

### Principles (binding for all of v1)

- This is a **personally used, long-term maintained** product — every feature below is justified by a real usage need, not resume keywords.
- **Reuse the v0 infrastructure:** the single `llm_client` gateway, the `llm_calls` table (its nullable `route`/`steps` columns get filled starting Phase 13), session isolation, per-session caps, and the LLM master switch. **No new parallel code paths for LLM calls.**
- **Explicit non-goals for all of v1:** LangGraph/LangChain, HITL gates, multi-agent, LLM-as-a-judge pipelines, fine-tuning, public/hosted MCP, eval dashboards, auth system.
- After Phase 15 closes, the project enters **demand-gated maintenance mode**: a new feature requires the same pain point 3+ times in real use; full feature freeze during application season (bug fixes only). This rule gets written into CLAUDE.md at close-out.

### v1 Phase Overview

| Phase | Content | Est. | Status |
|-------|---------|------|--------|
| 13 | Tool layer → hand-written agent loop → pipeline-vs-agent experiment → regression set | ~1 week | not started ← next |
| 13.5 | FastMCP local wrapper (stdio only) | 1 day | not started |
| 14 | RAG: ingestion → hybrid retrieval (pgvector + FTS→BM25, RRF) → cited reports | ~4 days | not started |
| 15 | Long-chat compression + indirect-injection defense | 2–3 days | not started |

Sequencing rationale: 13 before 14 because `search_news` becomes the retrieval entry point and the regression set must exist before RAG changes report behavior; 15 last because sanitization sits on top of the Phase 14 retrieval path.

### Phase 13 — Hand-Written Agent Loop + Pipeline-vs-Agent Experiment

**Goal:** an agent execution path alongside the existing fixed pipeline; measure both; route by request type.

1. **Tool layer** — wrap existing data-fetching as plain, individually testable functions with typed signatures + docstrings (docstrings become the tool schemas): `get_price_history(ticker, period)`, `get_financials(ticker)`, `search_news(ticker, query, limit)`, `compute_indicators(ticker, indicators)`, `extract_bulk(docs)` (routes internally to the flash-tier path — no duplicated logic). **Max 5 tools, all read-only.**
2. **The loop** — ~100 lines, single module: send messages + tool schemas → execute returned tool calls → append results → repeat → terminal when the model answers without tool calls. Guardrails: **max 8 steps** (overflow → best-effort partial answer + explicit "step limit reached" note), per-call timeout, tool errors fed back as tool results (never crash the request). All calls through `llm_client`; log `route='agent'`, `steps=<n>`; pipeline path logs `route='pipeline'`, `steps=NULL`. Keep the loop core readable — it's whiteboard material, no cleverness.
3. **Prompt caching** — the loop resends full history every step, so the static prefix (system prompt + tool schemas) is where the cost multiplier gets paid down. Structure prompts static-first (DeepSeek auto-caches by prefix; other providers need explicit breakpoints). Log cached-token counts in `llm_calls`; report the measured saving.
4. **Cost defenses** — verify the agent path is fully covered by session caps + the master switch (caps already count per LLM call, so no bypass).
5. **The experiment (the point of the phase)** — ~20 labeled cases in two request types (standard report / open-ended query). Run every case through both paths; collect **cost** (tokens × price, from `llm_calls`), **latency**, **quality** (manual key-fact checklist per case, scored by script). Deliverable: results table in the README + a routing decision in decisions.md; implement the request-type router accordingly. Expected shape (verify, don't assume): standard → pipeline, open-ended → agent.
6. **Regression set** — promote the 20 cases + scoring script into `eval/` with a one-command target. New CLAUDE.md rule at that point: any change to prompts, models, or retrieval parameters runs the regression set before merge; a score drop blocks the merge. Keep it ~20 cases — a maintenance tool, not a research harness.

**Acceptance:** agent path answers open-ended queries via tools with a visible tool-call trace; both routes fully covered by cost defenses; README shows the comparison table; regression set runs with one command.

### Phase 13.5 — MCP Wrapper (local stdio only)

Wrap the Phase 13.1 tool functions with **FastMCP**, local stdio transport — thin glue importing the same functions, zero duplicated logic. **Never deployed as a public/hosted MCP server** (it would bypass session caps and the master switch) — document the constraint in the deployment guide. Deliverable: `mcp_server.py` + a README registration snippet. **Acceptance:** a natural-language stock question from Claude Code invokes the local tools and returns real data.

### Phase 14 — RAG: Hybrid Retrieval + Cited Reports

**Goal:** reports grounded in retrievable sources with citations — the owner acts on these reports; unverifiable financial claims are unacceptable.

1. **Ingestion** — news/filings already reachable by the fetch layer; fixed-size chunking with overlap (tune only if the regression set shows problems) → embeddings → **pgvector on Neon** (no separate vector DB). Chunk metadata: source URL, title, published date, ticker.
2. **Hybrid retrieval** — pgvector cosine + lexical path. Platform reality: pg_search/ParadeDB is **not available on Neon** — lexical = native Postgres FTS (tsvector + GIN) for the candidate pool, rescored in the app layer with `rank_bm25` so the scoring is genuinely BM25. Fuse with **RRF** (standard formula, k=60), pure and unit-tested. **Claim-precision rule:** say "BM25" only if BM25 actually runs; ts_rank-only ships as "keyword/full-text retrieval".
3. **Cited generation** — retrieved chunks carry stable IDs; the model attaches citation IDs to key claims; frontend renders citations as links (URL + title); uncited claims are visibly marked. Structured-output validation on citation format: one retry, then degrade gracefully — never a white screen.
4. **Verification** — run the Phase 13 regression set before/after; add ~5 citation-specific cases (presence + does the cited chunk actually support the claim). Retrieval cost/latency logged through the existing observability path.

**Acceptance:** reports show clickable citations; regression score did not drop; hybrid retrieval demonstrably returns results either path alone misses (one example in the PR description).

### Phase 15 — Context Compression + Indirect-Injection Defense

1. **Sliding window + summarization** — past a token threshold, keep the last N turns verbatim and compress older turns into a running summary via the flash-tier path; persist the summary across restarts. Threshold + N in settings. Log compression events (tokens before/after) to `llm_calls` (`kind='summarize'`); deliver a measured before/after cost number into the README.
2. **Retrieved-content sanitization** (OWASP LLM01 — poisoned public content must not steer reports the owner acts on): ① **demarcation** — retrieved chunks wrapped in delimited untrusted-data blocks, system prompt states block content is data, never instructions; ② **sanitization** — strip instruction-like patterns/markup that could break demarcation (fake role tags, "system:" prefixes); ③ **privilege boundary** — tools are read-only, so blast radius is report bias, not actions (record the reasoning in decisions.md). 2–3 poisoned-chunk regression cases; pass = the injected instruction is neither followed nor cited. **No LLM-based injection classifier** — demarcation + sanitization + read-only tools is the right depth for this threat model.

**Acceptance:** long chats compress with logged savings; poisoned-chunk cases pass; decisions.md documents the threat model and defense depth.

### v1 Close-Out (after Phase 15)

- README: architecture diagram gains the agent loop / MCP / RAG paths; experiment + compression numbers present; demo-limits note current.
- decisions.md covers: hand-written loop vs LangGraph (recorded up front as Decision 010), mixed routing policy, hybrid retrieval design, injection threat model, MCP local-only constraint.
- CLAUDE.md gains the demand-gated maintenance rule + the regression-set merge gate.
- CHANGELOG closes v1; project enters maintenance mode.

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

---

*Detailed per-phase scope/decision records for completed phases live in `CHANGELOG.md` — this file stays lean and forward-looking. The v1 plan above supersedes the earlier "post-v0 direction" sketches in `docs/planning/` where they conflict.*
