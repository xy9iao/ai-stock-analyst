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
| 13 | Tool layer → hand-written agent loop (Research Agent) → regression set | ~1 week | not started ← next |
| 13.5 | FastMCP local wrapper (stdio only) | 1 day | not started |
| 14 | RAG: ingestion → hybrid retrieval (pgvector + FTS→BM25, RRF) → cited reports | ~4 days | not started |
| 15 | Long-chat compression + indirect-injection defense | 2–3 days | not started |

Sequencing rationale: 13 before 14 because `search_news` becomes the retrieval entry point and the regression set must exist before RAG changes report behavior; 15 last because sanitization sits on top of the Phase 14 retrieval path.

### Phase 13 — Research Agent (hand-written tool-use loop)

**What it is.** *Research Agent* — an on-demand due-diligence engine. The owner asks an open-ended market question ("why did NVDA drop this week?", "is this dip NVDA-specific or sector-wide?"); the agent decides which evidence to pull from the app's own data plane, loops until answered (max 8 steps), and files an archived research memo alongside pipeline reports. It gathers and synthesizes evidence; it never issues trade instructions (the existing advice boundary stays in the system prompt verbatim).

**Why an agent (design argument, recorded — the pipeline-vs-agent experiment is removed; the eval-harness project owns the "experiments" story).** Standard reports have *closed* data needs — what a `single_stock`/`portfolio` report requires is fully known at design time, so the fixed pipeline is strictly cheaper and more consistent there. Open-ended research has *forked* evidence paths — whether to pull a competitor's history, read article bodies, or check earnings dates depends on what the previous step revealed. A loop hands that conditional control flow to the model. Routing is therefore a **design decision by request type** (Decision 011): closed data needs → pipeline (`route='pipeline'`); open-ended forensics → agent (`route='agent'`).

**Primary use cases (these seed the regression set):** ① move attribution (price swing → evidence memo); ② pre-decision evidence check before adding/trimming a position (evidence list, never a verdict); ③ earnings-cycle synthesis (expectations before, reaction after); ④ cross-ticker comparison ("me vs sector"); ⑤ themed news synthesis with bulk reading.

**Product contract — Research vs Chat vs Reports (Decision 011).** Three verbs, three service tiers; they compose, they do not merge:

| | Trigger | Data access | Cost/latency | Output |
|---|---|---|---|---|
| Report (pipeline) | button, fixed type | fixed context package | 1 call | archived report |
| **Research (agent)** | free-text question | loop-driven evidence gathering, ≤8 steps | ~10 calls, tens of seconds | archived memo |
| Chat | conversation | fixed toggleable context injection | 1 call/message, fast | ephemeral |

Anything worth archiving goes to Reports (pipeline = routine checkup, research = case investigation); casual questions go to chat. **Composition loop (already free):** chat's `include_recent_reports` toggle means *agent produces the artifact → chat consumes it* — run one research memo, follow up cheaply in chat. **Chat stays non-agentic — hard boundary:** per-message loops would kill chat's fast/cheap contract and burn the 20-call session cap in two messages. Do not wire the loop into chat.

**13.1 Tool layer (5 tools, locked).** Thin wrappers over existing **service-layer** functions (never providers/repositories directly — reuse cache-aside, ticker normalization, `AppError`): `get_price_history(ticker, period)` · `get_financials(ticker)` · `search_news(ticker, query, limit)` · `extract_bulk(docs)` (routes internally to the flash-tier path through `llm_client` — zero duplicated logic). Plus one new pure function: `compute_indicators(ticker, indicators)` (SMA/EMA/RSI, ~30 lines, no TA-Lib), in `ai/agent/indicators.py`. Typed signatures + docstrings (docstrings become the tool schemas). All read-only. **Max 5 — do not add tools mid-phase.**

**13.2 The loop (Core).** `ai/agent/loop.py`, ~100 lines, single module: send messages + tool schemas → execute returned tool calls → append results → repeat → terminal when the model answers without tool calls. Requirements: **max 8 steps** (overflow → best-effort answer + explicit "step limit reached" note); per-call timeout; **multiple tool calls in one turn handled correctly** (execute each, one tool message per `tool_call_id`); tool exceptions, timeouts, and malformed arguments each fed back as tool results (the loop continues; the request never 500s). All LLM calls through `llm_client` — the gateway gains a `tools` parameter and returns the full assistant message; the loop never instantiates its own client. Log `route='agent'`, `steps=<n>`. Whiteboard-readable, no cleverness.

**13.3 Prompt caching (Core: prefix placement).** The loop resends full history every step; the static prefix (system prompt + tool schemas) is where the cost multiplier gets paid down. Freeze the prefix at import time, order strictly static-first (DeepSeek caches by prefix automatically). **One migration this phase:** `llm_calls` gains nullable `cached_tokens`; `llm_client` records the provider's cache-hit count; `/api/stats` aggregates it. Deliverable: measured saving on a repeated-query demonstration.

**13.4 Integration & routing.** No new top-level module: `ai/agent/{loop,tools,indicators}.py`. Product entry reuses `POST /api/reports` with `report_type="research"` (body gains an optional `query`, required for `research`); the dispatch in `ai/router.py` *is* the request-type router — the code is an if-statement, the decision is Decision 011. Memos save through the existing reports repository (title = truncated query), render on the existing Reports page. **UI scope:** a Research query box at the top of the Reports page with a plain, honestly-labeled loading state (10–20s; no streaming) — that is all. **Not in scope:** chat integration (hard boundary), holdings/watchlist context injection (comparisons are asked explicitly by ticker), streaming/SSE, persisting tool traces to DB (logs only), unified input box / mode switcher.

**13.5 Cost-defense verification.** The agent path must be fully covered by existing defenses, with **worst-case math written in the PR description**: research memos count against the per-session report cap (≤3); one run ≤ 8 loop steps + nested `extract_bulk` flash calls → demo worst case ≈ 3 runs × ~10 LLM calls, bounded by max-steps, per-call cap accounting, and the master switch. No new infra.

**13.6 Regression set (a maintenance gate — NOT a benchmark, NOT an experiment).** ~20 labeled research-query cases spanning the five use cases: `{query, key_facts[]}`. Scoring = key-fact coverage via script (Core); the runner executes the **agent path only**, direct function calls (no HTTP), **local-run only** (never CI — real spend). Promote to `eval/` with a one-command target. CLAUDE.md rule (unchanged): any change to prompts, models, or retrieval parameters runs the set before merge; a score drop blocks the merge. Purpose: the owner uses this tool for real decisions — Phase 14/15 must not make it quietly dumber.

**Acceptance:** a research query from the UI produces an archived memo with a visible tool-call trace in logs; parallel tool calls, tool failures, malformed arguments, and step overflow all handled per 13.2 (three failure-injection tests exist); `cached_tokens` recorded and aggregated with a measured saving; worst-case cost math in the PR; regression set runs with one command.

**Demand-gated futures (recorded, NOT built — gate: same pain 3+ times in real use):** "Discuss this memo" button (opens chat with `include_recent_reports` pre-toggled) · unified input box with a Chat/Research mode switch · thesis patrol ("did this week's news shake my NVDA thesis?", using the dormant `investment_thesis` field).

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

- README: architecture diagram gains the agent loop / MCP / RAG paths; an example research memo + a regression-set usage note + the caching/compression numbers present; demo-limits note current.
- decisions.md covers: hand-written loop vs LangGraph (Decision 010), routing-by-request-type + non-agentic chat (Decision 011), hybrid retrieval design, injection threat model, MCP local-only constraint.
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
