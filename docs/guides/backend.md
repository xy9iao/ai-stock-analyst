# Backend Guide

This guide documents the backend as implemented in **v0** (feature-complete, 2026-07-02).

## Purpose

The FastAPI backend owns:

- database access
- external API access
- AI/LLM integration
- report generation
- chat logic
- secrets and environment configuration

The frontend should call backend API routes. It should not directly call PostgreSQL, market data APIs, news APIs, or LLM APIs.

## Current Structure

```txt
backend/
├── app/
│   ├── main.py              # FastAPI app + router registration (health, holdings, watchlist, market, news, financials, reports, chat)
│   ├── core/
│   │   ├── cache.py         # shared TTL cache (market data, news, financials)
│   │   ├── config.py        # typed pydantic-settings
│   │   ├── database.py      # engine, get_db session dependency, Base
│   │   ├── demo_session.py  # anonymous demo-session cookie middleware + TTL cleanup
│   │   ├── errors.py        # AppError + global handler
│   │   ├── llm_switch.py    # LLM master switch (settings-table row + TTL)
│   │   └── logging.py
│   ├── models/              # all SQLAlchemy models (one file per table)
│   └── modules/
│       ├── health/
│       │   └── router.py
│       ├── holdings/        # router → service → repository → schemas
│       │   ├── router.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── schemas.py
│       ├── watchlist/       # same layering as holdings
│       │   ├── router.py
│       │   ├── service.py
│       │   ├── repository.py
│       │   └── schemas.py
│       ├── market_data/     # provider abstraction + cache-aside (Phase 4)
│       │   ├── provider.py        # MarketDataProvider Protocol
│       │   ├── providers/         # yfinance_provider.py
│       │   ├── service.py         # cache-aside (uses core/cache.py)
│       │   ├── router.py
│       │   └── schemas.py
│       ├── news/            # company news (Phase 5)
│       │   ├── provider.py        # NewsProvider Protocol
│       │   ├── providers/         # yfinance_news_provider.py
│       │   ├── service.py
│       │   ├── router.py
│       │   └── schemas.py
│       ├── financials/      # financial snapshots (Phase 5)
│       │   ├── provider.py        # FinancialDataProvider Protocol
│       │   ├── providers/         # yfinance_financials_provider.py
│       │   ├── service.py
│       │   ├── router.py
│       │   └── schemas.py
│       ├── ai/              # AI report generation (Phase 6) + Research Agent (Phase 13)
│       │   ├── llm_client.py       # the single OpenAI-compatible LLM call site (chat/complete/chat_message)
│       │   ├── agent/              # hand-written tool-use loop (Phase 13)
│       │   │   ├── loop.py         #   run_research: ≤8-step evidence loop, frozen static prefix
│       │   │   ├── tools.py        #   5 read-only tool wrappers over service functions
│       │   │   └── indicators.py   #   SMA/EMA/RSI (pure functions)
│       │   ├── context.py          # compact DB-context assembly
│       │   ├── prompt_builder.py   # system prompt (style + safety) + user prompt
│       │   ├── report_generator.py # pipeline orchestration + research-memo entry
│       │   ├── repository.py       # reports table read/write
│       │   ├── router.py           # incl. the request-type dispatch (Decision 011)
│       │   └── schemas.py
│       ├── chat/            # investment chat assistant (Phase 7)
│       │   ├── context.py          # toggleable context assembly (reuses ai/context)
│       │   ├── service.py          # orchestration + scope control + demo cap
│       │   ├── repository.py       # chat_sessions / chat_messages
│       │   ├── router.py
│       │   └── schemas.py
│       ├── session/         # demo-session reset endpoint (Phase 12)
│       │   └── router.py
│       └── admin/           # LLM master switch (token-gated) + /api/stats (Phase 12)
│           ├── router.py
│           └── schemas.py
├── alembic/
├── eval/                    # Phase 13 regression set: cases.json + scoring + runner (local-only, real spend)
├── tests/                   # conftest.py (SQLite fixture) + test_*.py
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

## Modular Monolith Convention

The backend is a modular monolith.

Future business modules should live under `backend/app/modules/`.

Each feature module has four files (see `holdings/` and `watchlist/` for the reference implementation):

```txt
modules/<feature>/
├── router.py      # HTTP layer: routes, status codes, Depends(get_db)
├── service.py     # business logic: validation, not-found -> AppError(404)
├── repository.py  # the only layer that touches the DB Session
└── schemas.py     # Pydantic request/response models
```

SQLAlchemy models do **not** live in the module — all models are centralized in `backend/app/models/` (one file per table, re-exported in `models/__init__.py`). Modules call each other through normal Python imports and service functions, not internal network calls.

### Layered request flow

A write request flows straight down the layers and back:

`router` (parse + validate body via schema) → `service` (rules, ticker normalization, 404) → `repository` (SQLAlchemy `add`/`commit`/`refresh`) → ORM row → serialized through the `*Read` schema (`from_attributes=True`).

Boundary rules:

- Input validation lives in `schemas.py` (Pydantic) and fails fast with `422` — bad data never reaches the service or DB.
- "Not found" is a service decision: the repository returns `None`, the service raises `AppError(..., 404)`, and the global handler in `core/errors.py` formats the JSON.
- Partial updates use `PATCH` with `model_dump(exclude_unset=True)` so only the fields the client sent are changed.

## Configuration

Backend configuration lives in `backend/app/core/config.py`.

Use `pydantic-settings` for typed environment variables. `.env.example` documents expected variables, while local `.env` (repo root; `config.py` loads `../.env`) stores real local values and must not be committed.

Settings in use:

- `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `BACKEND_CORS_ORIGINS`
- `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (default `deepseek-v4-flash`) — consumed only by `modules/ai/llm_client.py`
- `MARKET_DATA_PROVIDER` (default `yfinance`) — selects the provider implementation

## Database

Database setup lives in `backend/app/core/database.py`: SQLAlchemy 2.x **sync** ORM style, with the shared declarative `Base`, engine creation from `settings.database_url`, the session factory, and the `get_db` FastAPI dependency that routes/repositories use. Tests override `get_db` with an in-memory SQLite session (see `tests/conftest.py`).

## Alembic

Alembic files live in `backend/alembic/` and `backend/alembic.ini`.

Alembic should read the same database URL as the app and use SQLAlchemy model metadata for autogeneration.

Common commands:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Error Handling

`backend/app/core/errors.py` defines `AppError(code, message, status_code)` plus a global handler. Services raise `AppError` for handled failures (e.g. not-found → 404, missing LLM key → 503); the handler formats the stable `{"detail": {"code", "message"}}` JSON body. No secrets or raw stack traces in normal responses.

## Logging

`backend/app/core/logging.py` provides a simple shared logging setup — readable local logs for startup, configuration, database, and API issues. Kept deliberately simple in v0.

## Demo hardening (Phase 12)

For the public demo (`DEMO_MODE=true`; off by default so local use is unchanged):

- **Anonymous session isolation** — `core/demo_session.py` middleware issues a `session_id`
  cookie; `holdings`, `watchlist_items`, `reports`, `chat_sessions` carry an indexed
  `session_id` column (`SessionScopedMixin`) and every repository filters by it. Local data
  lives in the permanent `"local"` bucket. Idle demo buckets are deleted after
  `DEMO_SESSION_TTL_DAYS` (lazy, throttled cleanup).
- **Cost defense (three layers):** ① DeepSeek prepaid balance = budget hard cap (operational);
  ② `core/llm_switch.py` — master switch stored in the `settings` table, default OFF, enabled
  via `POST /api/admin/llm` with a TTL, checked inside `llm_client` (the single gateway);
  ③ per-session caps in the `ai`/`chat` services, counted in **LLM calls** (agent-proof),
  derived from existing rows (no counter infra).
- **Observability** — `llm_client` writes one `llm_calls` row per call (tokens, latency,
  `cached_tokens`, and — on the agent path — `route='agent'` + the 1-based `steps` index)
  plus a structured log line; `GET /api/stats` aggregates them. Research memos count
  against the same per-session report cap as pipeline reports.

## Research Agent (Phase 13)

`POST /api/reports` with `report_type="research"` + `query` routes to the hand-written
tool-use loop in `modules/ai/agent/loop.py` (Decision 011: closed data needs → pipeline,
open-ended forensics → agent; chat stays non-agentic). The loop sends full history + the
5 tool schemas through `llm_client.chat_message`, executes returned tool calls
sequentially (one `role:tool` message per `tool_call_id`), and terminates when the model
answers without tool calls, when the 8-LLM-call budget forces a final no-tools answer
(memo marked "step limit reached"), or when the gateway raises `AppError`. Tool errors —
unknown names, malformed arguments, service `AppError`s — are fed back as tool-result
text and never end the loop. The static prefix (system prompt + tool schemas) is frozen
at import so DeepSeek's prefix cache pays down the resend-full-history cost (~79% of
agent-path prompt tokens cache-served, measured 2026-07-17).

**Regression gate:** `backend/eval/` holds 20 labeled research cases scored by
deterministic key-fact coverage (`uv run python -m eval.run`; `--record` moves the
baseline) plus 5 citation cases (`--citations`: the cited chunk must contain the
expected atom). Local-only, never CI. Per CLAUDE.md, any change to prompts, models,
or retrieval parameters runs it before merge; a score below baseline − tolerance
blocks. Imperfect-case memos land in `eval/.last_failures.md` (gitignored) for
diagnosis; `uv run python -m eval.corpus <term>` inspects the ingested corpus.

## Hybrid RAG + Cited Reports (Phase 14)

`modules/ai/rag/` — one retrieval code path serving two consumers: the pipeline's
fixed retrieval step (single-stock reports) and the agent's `search_documents` tool.

- **Ingestion** (`ingest.py`) — news URLs → trafilatura body extraction →
  `chunking.chunk_text` (1800 chars, 200 overlap, sentence/whitespace boundary
  snapping; deterministic so `(source_url, chunk_index)` stays citation-stable) →
  `embeddings_client.embed_texts` (OpenAI `text-embedding-3-small`, the single
  embedding call site, `kind='embed'` rows in `llm_calls`) → `document_chunks`
  (pgvector `vector(1536)`). Idempotent per URL (delete-then-insert); per-doc
  failures are logged and skipped.
- **Retrieval** (`retrieval.py`) — `hybrid_search`: pgvector cosine scan (no ANN
  index — corpus-size call) + Postgres FTS candidate pool (OR-joined
  `websearch_to_tsquery` for recall, GIN expression index) rescored with real BM25
  (`rank_bm25`, pool-relative IDF), fused with RRF (k=60, rank-based, fuse before
  truncating to top-8; agent tool takes top-5). Vector-path failure degrades to
  lexical-only — retrieval never takes a report down.
- **Citations** (`citations.py`) — prompts inject Sources blocks tagged
  `[chunk:id]`; the model cites by copying tags. Save-time rewrite turns valid tags
  into numbered links + a `## Sources` section in the stored Markdown (citations
  survive export); validation is deterministic set-membership (pipeline: retrieved
  set + one corrective retry; agent: DB existence — weaker, known limit); invalid
  tags are stripped with a visible note, `[unverified]` renders as a badge.

## Testing

`backend/tests/` holds the pytest suite (145 tests): `conftest.py` provides a `client` fixture backed by in-memory SQLite via a `get_db` override; market/news/financials providers and the LLM are monkeypatched at their factory/call seams, so tests run with **no network and no API cost**. `uv run pytest` also reports coverage (`pytest-cov`, measured — not gated).

## Health Endpoint

`GET /api/health` → `{ "status": "ok", "service": "ai-stock-analyst-backend" }` — used by Docker/dev to confirm the API is up.
