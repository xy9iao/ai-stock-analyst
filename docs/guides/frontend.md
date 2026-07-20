# Frontend Guide

The frontend is a **Next.js 15 (App Router) + React 19 + TypeScript** app styled with **Tailwind CSS**, using local shadcn-style components. It is **presentation-only**: every backend call goes through `frontend/lib/api/`, and the app never talks to the database, LLM, or market/news APIs directly.

## Running it

- `pnpm dev` — dev server on :3000 with hot reload (the fast inner loop).
- `pnpm typecheck` / `pnpm lint` / `pnpm build` — the three CI gates; run before committing.
- For data, run the backend + Postgres (e.g. `docker compose up postgres backend`); `pnpm dev` proxies `/api/*` to the backend (see `next.config.ts`). Reserve `docker compose up --build` for full-stack/integration checks, not day-to-day iteration.

## Testing

**Vitest + React Testing Library** (jsdom). `pnpm test` runs the suite (a CI gate); `pnpm test:coverage` reports coverage. Tests live next to what they cover (`*.test.ts` / `*.test.tsx`).

Covered:

- **Utils** — `lib/format`, `lib/download` (pure functions).
- **API boundary** — `lib/api/*` with a mocked `fetch` (right endpoint/method; throws the backend message on non-2xx; `undefined` on 204).
- **Components** — `Button` variants, `EmptyState`.
- **Page integration** — `HoldingsPage` renders each of the four data states (loading / load-error / empty / data) via mocked `lib/api/*`.

Two gotchas for page tests: wrap the render in `TooltipProvider` (pages with `InfoTip` need it — the app mounts one in `layout.tsx`), and mock `next/link` with a passthrough.

## Structure

- `app/` — App Router pages: `/` (dashboard), `/holdings`, `/watchlist`, `/reports` (pipeline reports + the Phase 13 Research query box — free-text question → agent memo, plain loading state, no streaming), `/chat`, `/stocks/[ticker]`. `layout.tsx` mounts the shared `TopNav`, `Footer`, the tooltip provider, and the toast `Toaster`.
- `components/`
  - `ui/` — the design-system primitives (below).
  - `layout/` — `TopNav`, `Footer`.
  - `reports/` — `MarkdownReport` (react-markdown + GFM + Tailwind typography).
  - `charts/` — `StockPriceChart` (recharts).
- `lib/`
  - `api/` — the typed backend client (`client.ts` + one module per resource). **All** backend calls live here.
  - `utils.ts` — `cn()` (clsx + tailwind-merge). `format.ts` — money/percent formatting. `download.ts` — client-side file export.

## Design system

Clean & minimal. **Slate** neutrals, **emerald** accent (primary actions, active nav, "up"), **red** for danger / "down". Controls use `rounded-md`, cards `rounded-lg`, surfaces `shadow-sm`.

### Primitives (`components/ui/`)

- **`Button`** — `cva` variants: `primary` (emerald CTA), `secondary` (neutral default), `ghost` (low-emphasis, e.g. Edit), `danger` (solid red, e.g. Delete); sizes `default` / `sm`.
- **`Card`** — white panel (border + shadow). **`Input`** — the single text control. **`Badge`** — status pill (`neutral` / `accent` / `danger`).
- **`Skeleton`** — pulsing load placeholder. **`EmptyState`** — centered "nothing here / couldn't load" block.
- **`Tooltip`** (radix) + **`InfoTip`** — an ⓘ icon that explains a finance term on hover/focus. Requires the `TooltipProvider` mounted in `layout.tsx`.

### Patterns

- **Four data states.** List/detail views render exactly one of: loading → `Skeleton`; load error → `EmptyState`; empty → `EmptyState`; data → the table/content. Load errors keep an `error` state; transient **action** failures (create/update/delete/generate/send) surface as **toasts**, not inline boxes.
- **Toasts** — `sonner` (`toast.error(...)`); `Toaster` mounted once in `layout.tsx` (`richColors`, bottom-right).
- **Nav** — `TopNav` is a sticky bar. Desktop: the logo links home + inline section links, with an emerald pill on the active route (nested routes like `/stocks/NVDA` don't light a section). Mobile: it collapses to the logo, which toggles a dropdown menu of all links.
- **Disclaimer** — `Footer` carries the "research, not financial advice" line on every page (reinforcing the LLM's system-prompt safety boundary in the UI).

## Conventions

- Every backend call goes through `lib/api/` — components never `fetch` the backend directly, and never reach the DB/LLM/market/news APIs.
- Money/quantities arrive from the API as Decimal **strings**; parse only for display (`lib/format.ts`) and keep the backend authoritative.
- `@/*` aliases the frontend root.
- New shared UI → `components/ui/`; keep it composable and `className`-overridable via `cn()`.
- Dark mode is deferred.
