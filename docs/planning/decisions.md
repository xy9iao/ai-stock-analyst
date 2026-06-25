## 1. Purpose

This document records important project decisions and the reasoning behind them.

The goal is to keep the project direction clear and avoid repeatedly reopening the same decisions without reason.

Each decision should include:

- Decision title
- Date
- Decision
- Reasoning
- Consequences

---

# Decision 001: Use Obsidian for planning and project repository for implementation

## Date

2026-06-11

## Decision

Use Obsidian as the planning and thinking space for the AI Stock Analyst project.

The actual project repository will contain implementation-facing documentation such as README, architecture docs, API docs, database schema docs, and development instructions.

## Reasoning

Obsidian is better for evolving thoughts, project planning, research notes, and design exploration.

The GitHub repository should stay cleaner and focus on what other developers or recruiters need to understand, run, and evaluate the project.

## Consequences

Planning notes will live in:

```txt
Projects/AI Stock Analyst/
```

Implementation will later live in:

```txt
ai-stock-analyst/
```

The Obsidian notes may contain broader thinking, future ideas, personal investment preferences, and rough design notes.

The project repository should contain polished and implementation-facing documentation.

---

# Decision 002: Use React + FastAPI + PostgreSQL + Docker as the MVP stack

## Date

2026-06-11

## Decision

Use the following MVP technology stack:

- Frontend: React
- Backend: FastAPI / Python
- Database: PostgreSQL
- Containerization: Docker and docker-compose

TypeScript should be considered for the frontend to make the project more maintainable.

## Reasoning

React is a strong choice for building a web dashboard with pages such as Dashboard, Holdings, Watchlist, Stock Detail, Chat, and Settings.

FastAPI is a good fit for AI application development because the project will involve Python-based data processing, external API integration, LLM calls, and structured API design.

PostgreSQL is a mature relational database that can store holdings, watchlist items, reports, chat history, stock notes, and cached market data.

Docker helps make the project easier to run locally and prepares it for future deployment.

## Consequences

The project will likely use a frontend/backend separated structure:

```txt
ai-stock-analyst/
├── frontend/
├── backend/
├── docker-compose.yml
└── README.md
```

The backend will be responsible for all external API calls, including market data APIs, news APIs, and LLM APIs.

The frontend will only communicate with the backend.

---

# Decision 003: Use a modular monolith first, not full microservices

## Date

2026-06-11

## Decision

Use a modular monolith architecture for the MVP.

The backend will be one FastAPI application, but the code will be organized into clear modules.

Possible modules include:

- Holdings
- Watchlist
- Market Data
- News
- Reports
- Chat
- AI

## Reasoning

The project should be designed like a real-world web service, but the MVP should not be overcomplicated.

Full microservices would introduce unnecessary complexity:

- More deployment work
- More network communication
- More authentication complexity
- More debugging difficulty
- More logging and monitoring requirements
- Slower MVP progress

A modular monolith gives many of the benefits of clean architecture while keeping development manageable.

## Consequences

The backend should be organized like this:

```txt
backend/
└── app/
    ├── core/
    └── modules/
        ├── holdings/
        ├── watchlist/
        ├── market_data/
        ├── news/
        ├── reports/
        ├── chat/
        └── ai/
```

Each module should have clear responsibility.

If the project grows, modules such as Market Data, News, or AI Analysis can be extracted into independent services later.

---

# Decision 004: Keep the AI module inside the backend for MVP

## Date

2026-06-11

## Decision

Keep the AI module inside the FastAPI backend for the MVP.

The AI module should include:

- Prompt building
- LLM API calls
- Report generation
- Chat response generation
- Recommendation boundary handling
- AI response parsing

## Reasoning

The MVP does not need a separate AI microservice.

Keeping AI logic in the backend makes the first version easier to build, test, and debug.

The frontend should not call the LLM API directly because:

- API keys must not be exposed in the browser.
- Prompt construction should be controlled by the backend.
- User holdings and watchlist context should be added safely.
- Reports and chat history should be stored in the database.
- Model switching should be handled centrally.

## Consequences

The initial AI module may look like this:

```txt
backend/
└── app/
    └── modules/
        └── ai/
            ├── prompt_builder.py
            ├── llm_client.py
            ├── report_generator.py
            ├── analysis_service.py
            └── schemas.py
```

In the future, this module can be extracted into a separate `ai-service` if needed.

---

# Decision 005: Use PostgreSQL as the MVP database

## Date

2026-06-11

## Decision

Use PostgreSQL as the database for the MVP.

## Reasoning

PostgreSQL is suitable for this project because it supports structured data such as:

- Holdings
- Watchlist items
- Reports
- Chat sessions
- Chat messages
- Stock notes
- Investment thesis
- Cached market data
- Settings

It is also a good long-term choice because the project may later support:

- User accounts
- Multiple portfolios
- Report history
- Investment profiles
- Alerts
- More advanced AI features
- Possible vector search through PostgreSQL extensions

## Consequences

The MVP should include database migration tooling.

The recommended backend database stack is:

- PostgreSQL
- SQLAlchemy
- Alembic

The database should run locally through Docker during development.

---

# Decision 006: Design for future web deployment, but keep MVP local-first

## Date

2026-06-11

## Decision

The MVP will be local-first, but the architecture should not block future web deployment.

## Reasoning

The first version is mainly for personal use and local development.

However, the long-term vision may include:

- Public website deployment
- Domain name
- User accounts
- Family/friend usage
- Beginner investor mode
- Subscription features

Therefore, the MVP should avoid patterns that would make future deployment difficult.

## Consequences

The project should use:

- Environment variables
- `.env.example`
- Docker
- Frontend/backend separation
- Backend-only external API calls
- Database migrations
- No hardcoded secrets
- No frontend exposure of API keys
- Modular backend structure

The MVP does not need production infrastructure yet, but it should be written in a way that can evolve toward production.

---

# Decision 007: Use provider abstraction for market data

## Date

2026-06-11

## Decision

The market data layer should be provider-agnostic.

The backend should not tightly couple business logic to one market data API.

## Reasoning

The project may start with free or easy-to-use data sources, but future versions may switch to more formal or paid APIs.

Possible data providers include:

- yfinance
- Finnhub
- Financial Modeling Prep

Provider abstraction allows the project to change data sources without rewriting the entire application.

## Consequences

The market data module should define a common interface, such as:

```txt
MarketDataProvider
    ├── get_quote(ticker)
    ├── get_price_history(ticker, range)
    ├── get_company_profile(ticker)
    └── get_market_index(index)
```

Provider implementations can be swapped later.

---

# Decision 008: Keep MVP focused on analysis, not trade execution

## Date

2026-06-11

## Decision

The MVP will only provide AI-generated stock analysis and investment suggestions.

It will not execute trades or connect to brokerage accounts.

## Reasoning

The project is designed as an AI-powered stock research assistant, not an automated trading bot.

Trade execution would introduce additional complexity, risk, security requirements, and financial responsibility.

## Consequences

The MVP will not include:

- Brokerage integration
- Real-money trade execution
- Automated trading
- Account balance synchronization
- Order placement
- Options/futures/crypto trading

The system may provide action labels such as Buy, Hold, Reduce, Sell, or Wait, but these are analysis outputs only.

The user remains responsible for final investment decisions.