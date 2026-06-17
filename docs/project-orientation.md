# AI Stock Analyst v0 MVP Orientation

Use this document as the starting prompt/context for building version 0 of AI Stock Analyst.

This project is currently in planning stage. The existing Obsidian planning files define the product vision, requirements, user stories, architecture, data strategy, AI behavior, roadmap, decisions, open questions, and Phase 1 implementation plan.

The next Codex session should use this file as the condensed project orientation and begin implementation from Phase 1.

This is also the user's first serious full-stack development project. The implementation should therefore teach and document normal professional development workflow while building the app. Do not assume the user already knows GitHub repository workflow, Python virtual environments, dependency management, Docker Compose, CI/CD, migrations, linting, formatting, or test commands.

---

## 1. Product Summary

AI Stock Analyst is a local-first AI-powered stock research assistant.

The product helps a beginner investor understand:

- What happened in the market
- Why major indexes or stocks moved
- What news matters
- How current holdings are doing
- Which watchlist stocks need attention
- Whether an action such as hold, add gradually, wait, reduce, sell, or research further may be reasonable

The application is for investment research and decision support only.

It is not:

- An automated trading bot
- A brokerage app
- A real-money trade execution system
- A guaranteed financial advice tool

The MVP should focus on long-term investment research, with light support for swing trading analysis.

The ideal product identity is:

> A beginner-friendly AI investment research assistant that helps users understand the market, analyze holdings, and make more informed investment decisions.

---

## 2. Target User

The initial target user is the project owner.

The user is interested in:

- U.S.-listed stocks
- S&P 500 companies
- Nasdaq-listed companies
- Major technology companies
- AI and high-growth tech names
- Active and high-volume stocks
- Resource-related companies
- Gold and silver-related assets
- Long-term investing
- Dollar-cost averaging
- Occasional swing trading opportunities

The user may not have time to manually read market news, charts, earnings updates, and macro developments every day.

The app should reduce fragmented market information into clear, practical, AI-generated analysis.

---

## 3. MVP Scope

Version 0 should be a local-first full-stack web application.

The MVP should support:

- Single local user
- Holdings management
- Watchlist management
- Market data display
- Basic stock chart display
- On-demand AI report generation
- Individual stock analysis
- Portfolio and watchlist analysis
- Investment-focused chat assistant
- Local settings for API keys and model configuration
- Report or chat export, preferably Markdown

The MVP should not support:

- Multi-user public deployment
- Brokerage connection
- Real-money trade execution
- Automated trading
- Options, futures, crypto, or forex
- Advanced quantitative backtesting
- Subscription or payment system
- Email report delivery
- Mobile or desktop app adaptation
- Internal stock prediction model training

---

## 4. Main Pages

The MVP should include these pages.

### Dashboard

Main landing page.

Shows:

- Major market index movement
- Portfolio summary
- Watchlist summary
- Latest generated report
- Important market or stock alerts
- Quick actions for AI analysis

The Dashboard should allow the user to request an overall market and portfolio report.

### Holdings

Manages stocks the user already owns.

Each holding requires:

- `ticker`
- `shares`
- `average_cost`

Optional fields:

- `company_name`
- `sector`
- `notes`
- `target_allocation`
- `investment_thesis`

The page should show:

- Current price
- Price change
- Percentage change
- Market value
- Unrealized profit or loss
- Basic chart preview
- AI action label
- Button to request holdings analysis

### Watchlist

Manages stocks the user wants to track but does not necessarily own.

Each watchlist item should include:

- `ticker`
- `company_name`
- `sector`
- `reason_to_watch`
- `notes`

The page should show:

- Current price
- Price change
- Percentage change
- Basic chart preview
- AI action label
- Button to request watchlist analysis

### Stock Detail

Shows detailed information for one ticker.

The user can open it from Holdings, Watchlist, or Dashboard.

It should display:

- Ticker
- Company name
- Sector
- Current price
- Daily price change
- Percentage change
- Basic chart
- Recent news
- Notes
- Investment thesis
- Latest AI analysis
- Button to request single-stock analysis

### Reports

Stores generated AI reports.

Report types:

- Overall Market + Portfolio Report
- Holdings Analysis Report
- Watchlist Opportunity Report
- Single Stock Analysis Report

Reports may appear first as recent report sections rather than a full main page.

### Chat

Investment-focused AI chatbot.

It should answer questions about:

- Stocks
- Investing
- Market news
- User holdings
- Watchlist
- Macro events
- Company analysis
- Generated reports
- Beginner financial education
- Prompt writing for other financial models

It should reject or redirect unrelated general-purpose questions.

### Settings

Stores local configuration such as:

- Market data API key
- News API key
- LLM API key
- Default AI model
- Preferred report style
- Default market focus
- Refresh behavior

Settings can stay simple in v0.

---

## 5. Core User Flows

### Flow 1: Daily Holdings Check

The user opens the app, reviews holdings, requests a holdings report, and reads action-oriented analysis.

Expected output:

- Portfolio summary
- Major gainers and losers
- Important news related to holdings
- Price movement explanation
- Suggested action labels
- Long-term investment view
- Short-term swing view
- Risk notes
- Follow-up questions

### Flow 2: Investment Decision Support

The user opens Dashboard, requests an overall market and portfolio report, and uses it to decide whether to buy, add, hold, reduce, sell, or wait.

Expected output:

- Overall market environment
- S&P 500 and Nasdaq summary
- Macro news summary
- Holdings analysis
- Watchlist opportunity analysis
- Suggested action for important stocks
- Portfolio-level risks
- Stocks needing further research

### Flow 3: Learning and Research Through Chat

The user asks investment-related questions in Chat.

The chatbot should answer directly first, then explain in beginner-friendly terms.

Example questions:

- What does P/E ratio mean?
- Based on my holdings, should I adjust anything?
- Which watchlist stock should I pay attention to?
- What happened in the market today?
- Why did the Nasdaq fall today?
- Should I add gradually or wait for a pullback?

### Flow 4: Single Stock Analysis

The user opens a stock detail page and requests AI analysis.

Expected output:

- Company summary
- Recent price movement
- Recent news
- Bullish factors
- Bearish factors
- Long-term investment view
- Short-term swing view
- Suggested action
- Confidence level
- Risk level
- Beginner-friendly explanation

### Flow 5: Manual Data Entry

The user manually adds holdings and watchlist items.

Manual entry is enough for v0.

Future versions may support CSV import, broker export import, screenshot import, or table copy-paste.

### Flow 6: Export

The user exports a report or chat history.

Preferred v0 export format:

- Markdown

This should work well with Obsidian.

---

## 6. Architecture

Use a production-ish modular monolith.

The MVP should be simple enough to build locally but structured so it can later support public deployment, user accounts, more providers, richer AI modules, and report history.

Recommended stack:

- Frontend: Next.js App Router + React + TypeScript + Tailwind CSS + shadcn/ui
- Backend: FastAPI + Python + Pydantic + SQLAlchemy + Alembic
- Database: PostgreSQL
- AI integration: backend-managed OpenAI-compatible client
- Infrastructure: Docker + docker-compose + environment variables

High-level architecture:

```txt
User Browser
    -> Next.js React Frontend
    -> FastAPI Backend
    -> Application Modules
        -> Holdings
        -> Watchlist
        -> Market Data
        -> News
        -> Reports
        -> Chat
        -> AI
    -> PostgreSQL

External APIs
    -> Market Data API
    -> News API
    -> LLM API
```

The frontend must not directly call:

- LLM APIs
- Market data provider APIs
- News APIs
- Database

All external API and database access should go through the backend.

---

## 7. Backend Structure

Recommended backend structure:

```txt
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── errors.py
│   ├── modules/
│   │   ├── health/
│   │   ├── holdings/
│   │   ├── watchlist/
│   │   ├── market_data/
│   │   ├── news/
│   │   ├── reports/
│   │   ├── chat/
│   │   └── ai/
│   └── tests/
├── alembic/
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── README.md
```

Each business module should generally contain:

- `router.py`
- `service.py`
- `repository.py`
- `models.py`
- `schemas.py`

Use service calls inside the monolith, not network calls between modules.

---

## 8. Initial Database Tables

The MVP database should eventually include:

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

Future versions may add:

- `users`
- `portfolios`
- `transactions`
- `investment_profiles`
- `subscriptions`
- `alerts`

Use PostgreSQL from the beginning.

Use Alembic migrations.

For v0, synchronous SQLAlchemy is preferred unless there is a strong reason to use async.

---

## 9. Data Source Strategy

The MVP focuses on the U.S. stock market.

Required data categories:

- Market index data
- Stock quote data
- Historical price and volume data
- Company news
- Macro market news
- Earnings or financial snapshot data
- Company profile data
- User holdings and watchlist data

Required indexes:

- S&P 500
- Nasdaq Composite or Nasdaq 100

Candidate providers:

- Financial Modeling Prep
- Finnhub
- yfinance as prototype fallback
- Alpha Vantage as later option

Recommended v0 approach:

1. Build provider interfaces first.
2. Use `yfinance` as a local prototype fallback if needed.
3. Keep code ready to switch to Finnhub or Financial Modeling Prep.
4. Do not tightly couple business logic to one provider.

Example provider interface:

```txt
MarketDataProvider
    get_quote(ticker)
    get_price_history(ticker, range)
    get_company_profile(ticker)
    get_market_index(index)
```

News provider interface:

```txt
NewsProvider
    get_company_news(ticker, from_date, to_date)
    get_macro_news(topic, from_date, to_date)
```

Financial data provider interface:

```txt
FinancialDataProvider
    get_latest_financials(ticker)
    get_earnings_calendar(ticker)
    get_company_profile(ticker)
```

---

## 10. Caching and Token Strategy

Cache market data where useful to avoid excessive API calls.

Possible cache rules:

- Quote data: short cache window
- Chart data: longer cache window
- Company profile: long cache window
- Financial statements: long cache window
- News data: medium cache window

The MVP may store cached data in PostgreSQL.

Do not send raw API responses to the LLM.

Instead, build compact structured context packages.

News context should include:

- Headline
- Related ticker
- Published date
- Short summary or description
- Source name

Do not send full articles in v0.

Financial context should be compact:

- Revenue
- Revenue growth
- EPS
- EPS surprise if available
- Net income
- Gross margin
- Operating margin
- Free cash flow if available
- Latest earnings date
- Next earnings date

Do not send full financial statements in v0 unless necessary.

---

## 11. AI Design

The AI acts as an investment research assistant.

It should:

- Summarize market news
- Explain price movements
- Review holdings
- Review watchlist stocks
- Generate investment reports
- Answer investment-related questions
- Explain beginner stock concepts
- Suggest possible actions with reasoning

It should not:

- Claim guaranteed profit
- Present outputs as absolute financial advice
- Say the user must buy or sell
- Act as a trading bot
- Answer unrelated general-purpose questions in Chat

Use conclusion-first style:

1. Direct conclusion
2. Suggested action
3. Short reasoning
4. Long-term investment view
5. Swing trading view
6. Beginner-friendly explanation
7. Risks or uncertainty
8. Follow-up questions or next steps

Reports should be Markdown in v0.

Future versions may use structured JSON internally.

---

## 12. AI Report Types

### Overall Market + Portfolio Report

Generated from Dashboard.

Should include:

- Overall market summary
- S&P 500 movement
- Nasdaq movement
- Macro news
- Technology sector summary
- Holdings summary
- Watchlist summary
- Major risks
- Suggested actions
- Questions for further research

### Holdings Analysis Report

Generated from Holdings page.

Should include:

- Portfolio summary
- Position-level analysis
- Gain/loss explanation
- Risk exposure
- Long-term investment view
- Short-term swing view
- Suggested actions

### Watchlist Opportunity Report

Generated from Watchlist page.

Should include:

- Watchlist summary
- Important watchlist news
- Potential opportunities
- Risk factors
- Suggested stocks to research further
- Entry timing considerations

### Single Stock Analysis Report

Generated from Stock Detail page.

Should include:

- Company summary
- Recent price movement
- Recent news
- Bullish factors
- Bearish factors
- Long-term investment view
- Short-term swing view
- Suggested action
- Confidence level
- Risk level

---

## 13. Action Labels

Supported AI action labels:

- Strong Buy
- Buy
- Add Gradually
- Hold
- Wait
- Reduce
- Sell
- Avoid

Each action label should include:

- Reasoning
- Confidence level
- Risk level
- Suggested strategy

Strategy examples:

- Long-term DCA
- Hold and monitor
- Add on pullback
- Wait for better entry
- Reduce exposure
- Research further
- Short-term swing only
- Avoid for now

Use action labels carefully.

The AI should focus on important stocks, not mechanically analyze every stock in every report.

A stock is important if:

- It is in holdings
- It has a large price movement
- It has important news
- It affects portfolio heavily
- It is a major watchlist opportunity
- It is related to a broader market or sector movement
- It has meaningful earnings or financial updates

---

## 14. AI Safety Boundaries

Avoid language such as:

- Guaranteed profit
- Risk-free investment
- You must buy
- This will definitely go up
- This is financial advice

Prefer language such as:

- Based on available data
- A reasonable action may be
- Consider
- This suggests
- The risk is
- Confidence is low, medium, or high
- Further research is needed

The user remains responsible for final investment decisions.

---

## 15. Preferred Report Template

Use this general Markdown report structure:

```md
# Report Title

## 1. Direct Conclusion

Short summary of what the user should know first.

## 2. Suggested Actions

- Stock or portfolio item:
  - Action:
  - Strategy:
  - Confidence:
  - Reason:

## 3. Market Context

Brief explanation of S&P 500, Nasdaq, and macro news.

## 4. Key Stocks to Watch

Only include important holdings or watchlist stocks.

### Ticker

- What happened:
- Why it matters:
- Long-term view:
- Swing view:
- Suggested action:
- Confidence:

## 5. Beginner Explanation

Explain important concepts or market logic in simple language.

## 6. Optional Risks or Uncertainty

Only include this section when risks are meaningful.

## 7. Follow-Up Questions

Suggest useful questions the user may ask next.
```

---

## 16. Frontend Direction

The frontend should be a React web app built with Next.js App Router.

Next.js is still React. It is chosen for v0 because the project is intended to be a long-term personal product and portfolio-quality application, not only a quick local demo. Next.js gives the frontend a more production-shaped architecture through file-based routing, layouts, loading states, error boundaries, and clear server/client component decisions.

FastAPI remains the real backend. Next.js should be used for the frontend application, routing, layouts, UI, client interactivity, charts, forms, and report rendering. It should not replace FastAPI for database access, market data APIs, news APIs, LLM calls, secrets, report generation, or chat business logic.

Recommended v0 frontend stack:

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- lucide-react
- TanStack Query
- React Hook Form
- Zod
- Lightweight Charts
- react-markdown

Use v0 as a stack trial. These libraries are good defaults, but they should be integrated in a way that keeps migration possible later.

Migration-safe frontend rules:

- Wrap chart rendering inside `components/charts/StockPriceChart.tsx`.
- Wrap Markdown report rendering inside `components/reports/MarkdownReport.tsx`.
- Keep backend API calls inside `lib/api/`.
- Keep TanStack Query hooks inside `lib/queries/`.
- Keep Zod schemas inside `lib/schemas/`.
- Keep shared frontend business types inside `types/`.
- Use simple `shadcn/ui` table components first.
- Delay TanStack Table until holdings/watchlist tables need sorting, filtering, pagination, column visibility, or row selection.
- Avoid importing chart, Markdown, or data-fetching library details directly inside page components unless there is a clear reason.

Library responsibilities:

- `lucide-react`: icons for navigation, buttons, empty states, and action controls.
- `shadcn/ui`: owned UI component code for buttons, cards, dialogs, tabs, forms, inputs, selects, badges, tables, toast, and sidebar/sheet patterns.
- `Tailwind CSS`: styling system and layout utilities.
- `TanStack Query`: frontend server-state fetching, caching, retries, loading states, and invalidation.
- `React Hook Form`: form state and submission handling.
- `Zod`: frontend validation and typed form/API schemas.
- `Lightweight Charts`: stock price and volume charts.
- `react-markdown`: rendering AI-generated Markdown reports.

Main frontend responsibilities:

- Render pages
- Manage user interactions
- Call backend APIs
- Display holdings and watchlist data
- Display charts
- Display AI reports
- Display chat conversations
- Provide buttons for AI analysis

The MVP should feel like a usable investment assistant, not a marketing landing page.

For operational pages like Dashboard, Holdings, Watchlist, Stock Detail, Reports, Chat, and Settings:

- Prefer dense but clear layouts
- Avoid decorative marketing sections
- Use tables, tabs, buttons, filters, and cards only where useful
- Add loading states, error states, and empty states
- Keep beginner language clear

---

## 17. Current Decisions

Decisions already made:

1. Use Obsidian for planning and a separate project repo for implementation.
2. Use Next.js App Router + React + TypeScript for the frontend.
3. Use modular monolith first, not full microservices.
4. Keep AI module inside backend for MVP.
5. Use PostgreSQL as the MVP database.
6. Design for future web deployment, but keep MVP local-first.
7. Use provider abstraction for market data.
8. Keep MVP focused on analysis, not trade execution.
9. Treat v0 frontend libraries as a stack trial and keep them replaceable through wrapper components and hooks.
10. Use `uv` for Python dependency management and virtual environment workflow, not Poetry.
11. Use `pnpm` for frontend dependency management.
12. Include beginner-friendly development workflow documentation in v0.
13. Add basic GitHub Actions CI checks during Phase 1.
14. Use DeepSeek first through an OpenAI-compatible LLM client wrapper, while keeping the LLM provider easy to swap.

The current Obsidian planning folder is not the implementation repo.

The implementation repo should be named:

```txt
ai-stock-analyst
```

Suggested implementation repo structure:

```txt
ai-stock-analyst/
├── .github/
│   └── workflows/
├── frontend/
├── backend/
├── docs/
│   └── development-workflow.md
├── prompts/
├── scripts/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 18. Important Open Questions

These should be resolved during early implementation:

1. Which formal market data provider to use first: Finnhub or Financial Modeling Prep.
2. Whether `yfinance` should be used only for prototype fallback.
3. Exact market data refresh and cache durations.
4. Maximum news items sent to the LLM.
5. Exact financial snapshot fields based on provider availability.
6. Whether Reports should become a main navigation page.
7. Final action-label color mapping.
8. Whether to store reports only as Markdown or also structured JSON later.
9. Whether report generation should remain synchronous or move to background jobs later.

Recommended v0 defaults:

- Use Markdown-only reports first.
- Use synchronous report generation first.
- Use synchronous SQLAlchemy first.
- Avoid Redis in v0.
- Avoid RAG and agents in v0.
- Use simple context injection first.
- Use `yfinance` only as prototype fallback.
- Use DeepSeek first through an OpenAI-compatible LLM client wrapper.
- Keep LLM settings configurable through `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`.
- Use no authentication in v0 because the app is single-user and local-first.
- Use local Docker Compose only for v0 deployment/runtime.

---

## 19. Development Workflow Learning Goals

Because this is the user's first full-stack development project, v0 should explicitly include normal development workflow and tooling education.

The implementation should teach and document:

- How the GitHub repository is organized.
- How to use branches for feature work.
- How to make small commits with clear commit messages.
- How pull requests work, even if the project is mostly personal.
- How to keep `.env` secrets out of Git.
- How Python virtual environments work.
- How `uv` manages Python versions, dependencies, lockfiles, and virtual environments.
- How frontend dependencies are installed and locked.
- How Docker Compose runs frontend, backend, and PostgreSQL together.
- How Alembic migrations are created and applied.
- How to run backend tests with `pytest`.
- How to run linting and formatting with `ruff`.
- How GitHub Actions CI checks code automatically.
- How local development differs from future deployment.

Recommended development workflow stack:

- Repository hosting: GitHub.
- Git workflow: feature branches from `main`, small commits, pull requests for meaningful milestones.
- Python tooling: `uv` with `pyproject.toml` and `uv.lock`.
- Python environment: project-local virtual environment managed by `uv`.
- Backend quality: `pytest`, `ruff check`, `ruff format`.
- Frontend package manager: `pnpm`.
- Frontend quality: TypeScript checks and Next.js lint/build checks.
- Local services: Docker Compose.
- CI/CD: GitHub Actions for install, lint, test, and build checks.
- Secrets: `.env` locally, `.env.example` committed, real `.env` ignored.

Do not overcomplicate CI/CD in v0.

The first GitHub Actions workflow should only verify:

- Backend dependencies install.
- Backend lint passes.
- Backend tests pass.
- Frontend dependencies install.
- Frontend type/build check passes.

Deployment automation is not required for v0.

---

## 20. Development Roadmap

Build phases:

1. Planning and design
2. Repository and development environment setup
3. Backend and database foundation
4. Holdings and watchlist CRUD
5. Market data integration
6. News and financial data integration
7. AI report generation
8. Chat module
9. Export and logging
10. UI polish and beginner experience
11. Testing and quality
12. README and public repo documentation
13. Future deployment preparation

Recommended build order:

```txt
Planning
    -> Repo skeleton
    -> Backend + database foundation
    -> Holdings + Watchlist CRUD
    -> Market data integration
    -> News + financial snapshot integration
    -> AI report generation
    -> Frontend UI polish
    -> Chat
    -> Export
    -> Tests
    -> README and demo
```

---

## 21. Version 0 MVP Definition

The MVP is complete when the user can:

1. Run the app locally.
2. Add holdings manually.
3. Add watchlist stocks manually.
4. Fetch market data for those stocks.
5. View basic price and volume charts.
6. Request a market + portfolio report.
7. Request single-stock analysis.
8. Ask investment-related chat questions.
9. Export at least one report or log as Markdown.
10. Understand the AI recommendation and reasoning.

---

## 22. Immediate Next Task: Phase 1

The next Codex session should begin with Phase 1: Repository and Development Environment Setup.

Phase 1 goal:

Create the initial implementation repository, frontend app, backend app, PostgreSQL database, and Docker Compose setup.

Phase 1 is complete when:

- The implementation repository exists.
- The frontend can run.
- The backend can run.
- PostgreSQL can run.
- Docker Compose can start the local stack.
- The frontend can call the backend health check endpoint.
- Basic Git/GitHub workflow is documented.
- Python `uv` setup and virtual environment workflow are documented.
- Local development commands are documented.
- A simple GitHub Actions CI workflow exists for lint/test/build checks.

### Phase 1.1: Create Repository

Create a new repository named:

```txt
ai-stock-analyst
```

Add:

- `frontend/`
- `backend/`
- `docs/`
- `prompts/`
- `scripts/`
- `.github/workflows/`
- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- `README.md`
- `docs/development-workflow.md`

The `docs/` folder should contain implementation-facing documentation only.

The broader planning notes remain in Obsidian.

The initial `docs/development-workflow.md` should explain, in beginner-friendly terms:

- What Git and GitHub are used for in this project.
- What branches, commits, pull requests, and `main` mean.
- What a Python virtual environment is.
- Why the backend uses `uv`.
- How to install backend dependencies.
- How to install frontend dependencies.
- How to start the app locally.
- How to run tests, linting, formatting, migrations, and Docker Compose.
- What CI/CD means and what GitHub Actions checks in v0.

### Phase 1.2: Initialize Backend

Backend stack:

- Python
- uv
- FastAPI
- Uvicorn
- Pydantic
- pydantic-settings
- SQLAlchemy
- Alembic
- psycopg 3 PostgreSQL driver
- pytest
- Ruff

Initial backend structure:

```txt
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── modules/
│       └── health/
│           └── router.py
├── tests/
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

Use `uv` instead of Poetry for v0.

The backend should document these basic commands:

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format .
```

Required endpoint:

```txt
GET /api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "ai-stock-analyst-backend"
}
```

### Phase 1.3: Initialize Frontend

Frontend stack:

- Next.js App Router
- React
- TypeScript
- pnpm
- Tailwind CSS
- shadcn/ui
- lucide-react

Initial frontend structure:

```txt
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── ui/
│   ├── charts/
│   │   └── StockPriceChart.tsx
│   └── reports/
│       └── MarkdownReport.tsx
├── lib/
│   ├── api/
│   │   └── client.ts
│   ├── queries/
│   └── schemas/
├── types/
├── package.json
├── next.config.ts
└── Dockerfile
```

Required behavior:

- Show app title
- Show basic Dashboard page
- Show backend health check status
- Keep frontend API calls pointed at the FastAPI backend.
- Keep chart, Markdown, API query, and schema libraries behind wrappers or `lib/` modules.

### Phase 1.4: Add PostgreSQL

Use PostgreSQL as a Docker service.

Required environment variables:

```txt
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL
```

### Phase 1.5: Add Docker Compose

Required services:

```txt
docker-compose
    -> frontend
    -> backend
    -> postgres
```

Running this should start the local development stack:

```bash
docker compose up --build
```

Expected result:

- Frontend runs on local port.
- Backend runs on local port.
- PostgreSQL runs on local port.
- Frontend can reach backend `/api/health`.

### Phase 1.6: Add Basic README Draft

README should include:

- Project name
- Short description
- Tech stack
- Local development setup
- Docker Compose command
- Environment variable setup
- Backend `uv` setup commands
- Frontend `pnpm` setup commands
- Basic Git/GitHub workflow
- CI check explanation
- Current project status

The README does not need to be polished yet.

### Phase 1.7: Add Basic GitHub Actions CI

Add a simple GitHub Actions workflow under:

```txt
.github/workflows/ci.yml
```

The v0 CI workflow should check:

- Backend dependencies install with `uv sync`.
- Backend lint runs with `uv run ruff check .`.
- Backend tests run with `uv run pytest`.
- Frontend dependencies install.
- Frontend build or type check runs.

The workflow does not need deployment.

The purpose of CI in v0 is to teach the normal professional habit:

```txt
push code -> GitHub Actions runs checks -> fix failures before merging
```

---

## 23. Instruction for the Next Codex Session

Use this document as the complete v0 MVP orientation.

Start by creating the `ai-stock-analyst` implementation repository as a separate project from the Obsidian planning folder.

Do not build unrelated future features yet.

Implement Phase 1 first:

- Repo skeleton
- Backend health endpoint
- Frontend dashboard
- Frontend-to-backend health check
- PostgreSQL Docker service
- Docker Compose local stack
- `.env.example`
- `.gitignore`
- Draft README
- Beginner-friendly `docs/development-workflow.md`
- Basic `.github/workflows/ci.yml`

After Phase 1 works, continue to backend database foundation, then Holdings and Watchlist CRUD.
