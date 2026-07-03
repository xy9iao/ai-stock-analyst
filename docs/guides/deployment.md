# Deployment Guide

Deploys the public demo: **Vercel** (frontend) + **Render** free tier (backend, Docker) + **Neon** free tier (Postgres). Cost: ~$0/month. Time: ~30 minutes.

```
Browser ──► Vercel (Next.js)  ──/api proxy──►  Render (FastAPI, Docker)  ──►  Neon (Postgres)
                                                        └──►  DeepSeek API (prepaid)
```

The demo runs with `DEMO_MODE=true`, which turns on the protections that make an unauthenticated public app responsible:

- **Anonymous session isolation** — every visitor gets a cookie-scoped data bucket (7-day TTL). No accounts, no shared state pollution.
- **Cost defense, three independent layers:** ① DeepSeek **prepaid balance** = hard budget cap (top up a small amount; never enable auto-recharge) → ② the **LLM master switch** (off by default; enabling always carries a TTL) → ③ **per-session caps** (3 reports, 20 chat replies — counted in LLM calls, not requests).

## Step 0 — DeepSeek budget cap

In the [DeepSeek platform](https://platform.deepseek.com), top up only a small amount (e.g. $5–10) and do **not** enable auto-recharge. The prepaid balance is the outermost cost wall: even if everything else failed, spend cannot exceed it.

## Step 1 — Neon (database)

1. Create a free project at [neon.tech](https://neon.tech) (Postgres 16+).
2. Copy the connection string and convert it for SQLAlchemy/psycopg:
   `postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require`

## Step 2 — Render (backend)

1. [render.com](https://render.com) → New → **Web Service** → connect the GitHub repo.
2. Language **Docker**; Root Directory **`backend`**.
3. **Docker Command: leave empty.** The image's own CMD migrates then serves
   (`alembic upgrade head && uvicorn ... --port ${PORT:-8000}`) and honors the
   platform-injected `PORT`. Don't wrap a command here — Render's field has its
   own shell/tokenization quirks (`sh -c "..."` gets double-wrapped, and a bare
   `&&` chain is exec'd without a shell).
4. Environment variables:
   - `DATABASE_URL` — the Neon URL from Step 1
   - `LLM_BASE_URL=https://api.deepseek.com`, `LLM_API_KEY=...`, `LLM_MODEL=deepseek-v4-flash`
   - `DEMO_MODE=true`
   - `ADMIN_TOKEN=...` — generate one: `openssl rand -hex 24`
   - `BACKEND_CORS_ORIGINS=https://<your-app>.vercel.app` (CORS is mostly moot behind the same-origin proxy, but keep it tight anyway)
5. Deploy → note the URL, e.g. `https://ai-stock-analyst.onrender.com` → check `/api/health`.

## Step 3 — Vercel (frontend)

1. [vercel.com](https://vercel.com) → Add New Project → import the repo → Root Directory **`frontend`** (framework auto-detects Next.js).
2. Environment variable: `BACKEND_URL=https://<your-render-url>` — the Next.js rewrite proxies `/api/*` there server-side, so browser calls stay same-origin (cookies just work, CORS stays irrelevant).
3. Deploy → the public URL is your demo link.

## Step 4 — Verify

- Open the Vercel URL: pages load, holdings/watchlist are empty (fresh session bucket).
- Add a holding → appears with live prices. Open the site in a private window → empty again (isolation works).
- `GET /api/stats` → zeroed aggregates. Footer **"New demo session"** → data resets.
- Reports/chat return *"demo LLM is currently switched off"* — correct: the switch defaults OFF.

## Step 5 — Operating the LLM switch

Turn the LLM on before a demo/interview (auto-off after the TTL, default 60 min):

```bash
curl -X POST https://<render-url>/api/admin/llm \
  -H "X-Admin-Token: $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"enabled": true, "ttl_minutes": 60}'
# status: GET the same URL with the token; off: {"enabled": false}
```

## CI/CD

CI (ruff + pytest / typecheck + lint + test + build) gates every PR; Render and Vercel auto-deploy `main` on push. Since all work lands via PRs: **tests gate the merge, and the merge is the deploy.**

## Known trade-offs & TODOs

- **Cold start (accepted):** Render's free tier spins down after ~15 min idle; the first request then takes up to ~1 min.
  **TODO — application season:** upgrade the backend to Render's paid instance (~$7/mo) while actively interviewing so the demo link opens instantly; downgrade after.
- Neon free also auto-suspends (cold start is only ~1s — fine).
- Observability = structured logs (Render dashboard) + `/api/stats` (token/latency aggregates from the `llm_calls` table). No metrics stack by design.
