> **v0 Outcome (2026-07-02).** Built as designed — modular monolith, backend owns all external access, router→service→repository layering. **One deviation:** SQLAlchemy models are centralized in `backend/app/models/` (one file per table), *not* per-module as sketched below. Read this document for intent; the guides in `docs/guides/` describe the code as it exists.

## 1. Purpose

This document defines the initial system architecture for the MVP version of AI Stock Analyst.

The goal is to design the project as a real-world web service while keeping the MVP simple enough to build and maintain.

The architecture should support:

- Local-first development
- Future web deployment
- Modular backend design
- Clear separation between frontend, backend, database, market data providers, and AI analysis
- Future expansion into more advanced services

## 2. Architecture Philosophy

The MVP should follow a production-ish architecture.

This means the project should not be written as a quick demo or one-file prototype.

Even though the first version runs locally, the project should be structured in a way that can later support:

- Public web deployment
- User accounts
- More data providers
- More AI analysis modules
- Report history
- Portfolio tracking
- Future subscription features
- Future microservice extraction

However, the MVP should avoid unnecessary complexity.

The recommended approach is:

**Modular monolith first, microservices later if needed.**

## 3. Recommended Tech Stack

### Frontend

- React
- TypeScript
- Vite
- React Router
- A charting library to be decided later
- UI component library to be decided later

### Backend

- FastAPI
- Python
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL

### AI Integration

- Backend-managed LLM integration
- OpenAI-compatible API client
- Prompt builder layer
- Report generation service
- Chat service

### Infrastructure

- Docker
- docker-compose
- Environment variables
- `.env.example`
- Local development containers

## 4. High-Level System Diagram

```txt
User Browser
    ↓
React Frontend
    ↓ HTTP / REST API
FastAPI Backend
    ↓
Application Modules
    ├── Holdings Module
    ├── Watchlist Module
    ├── Market Data Module
    ├── News Module
    ├── Reports Module
    ├── Chat Module
    └── AI Module
    ↓
PostgreSQL Database

External APIs
    ├── Market Data API
    ├── News API
    └── LLM API
```

## 5. Frontend Architecture

The frontend should be a React web application.

The frontend is responsible for:

- Rendering pages
- Managing user interactions
- Calling backend APIs
- Displaying holdings and watchlist data
- Displaying charts
- Displaying AI reports
- Displaying chat conversations
- Providing buttons to request analysis

The frontend should not directly call:

- LLM APIs
- Market data provider APIs
- News provider APIs

All external API calls should go through the backend.

### Main Frontend Pages

The MVP frontend should include:

- Dashboard
- Holdings
- Watchlist
- Stock Detail
- Chat
- Settings

Reports may appear as:

- Recent report section on Dashboard
- Latest analysis section on Stock Detail
- Optional report history page

## 6. Backend Architecture

The backend should be a FastAPI application.

The backend is responsible for:

- Exposing REST APIs to the frontend
- Managing holdings
- Managing watchlist
- Fetching market data
- Fetching news data
- Building AI prompts
- Calling LLM providers
- Generating reports
- Storing reports and chat history
- Managing local settings
- Handling data provider abstraction

The backend should be modular.

Each major feature should have its own module.

## 7. Recommended Backend Module Structure

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
│   │   ├── holdings/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── watchlist/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── market_data/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── provider.py
│   │   │   ├── providers/
│   │   │   │   ├── yfinance_provider.py
│   │   │   │   ├── finnhub_provider.py
│   │   │   │   └── fmp_provider.py
│   │   │   └── schemas.py
│   │   ├── news/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── provider.py
│   │   │   └── schemas.py
│   │   ├── reports/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── chat/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   └── ai/
│   │       ├── prompt_builder.py
│   │       ├── llm_client.py
│   │       ├── report_generator.py
│   │       ├── analysis_service.py
│   │       └── schemas.py
│   └── tests/
├── alembic/
├── pyproject.toml
├── Dockerfile
└── README.md
```

## 8. Modular Monolith Design

The MVP should use a modular monolith architecture.

This means:

- There is one backend application.
- Each business area is organized as a separate module.
- Modules have clear boundaries.
- Each module contains its own router, service, repository, models, and schemas when needed.
- Modules communicate through Python service calls, not network calls.

This provides the benefits of modular design without the operational complexity of microservices.

## 9. Future Microservice Direction

If the project grows, some modules may be extracted into separate services.

Possible future services include:

- Market Data Service
- News Service
- AI Analysis Service
- Report Generation Service
- Notification Service
- User Profile Service

The MVP should not implement these as separate services yet.

The code should simply be structured so extraction is possible later.

## 10. Database Architecture

The MVP should use PostgreSQL.

PostgreSQL is suitable because the project needs to store structured data such as:

- Holdings
- Watchlist items
- Reports
- Chat conversations
- Stock notes
- Investment thesis
- Cached market data
- Local settings

The database should be accessed through the backend only.

The frontend should never directly access the database.

### Initial Database Tables

The MVP may include:

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

Future versions may include:

- `users`
- `portfolios`
- `transactions`
- `investment_profiles`
- `subscriptions`
- `alerts`

## 11. Data Provider Architecture

The market data layer should be provider-agnostic.

The backend should not hardcode business logic directly against one market data API.

Instead, the system should define a provider interface.

Example:

```txt
MarketDataProvider
    ├── get_quote(ticker)
    ├── get_price_history(ticker, range)
    ├── get_company_profile(ticker)
    └── get_market_index(index)
```

Possible providers:

- yfinance provider for prototype fallback
- Finnhub provider
- Financial Modeling Prep provider

The system should allow replacing one provider with another without rewriting the entire application.

## 12. AI Architecture

The frontend should not call the LLM API directly.

All AI requests should go through the backend.

This is important because:

- LLM API keys must not be exposed in the browser.
- Prompt construction should be controlled by the backend.
- User holdings and watchlist context should be added safely.
- Generated reports should be stored in the database.
- Future model switching should be easier.
- Safety boundaries should be enforced in one place.

### AI Module Responsibilities

The AI module should handle:

- Building prompts
- Calling the LLM provider
- Parsing AI responses
- Generating reports
- Generating chat replies
- Applying recommendation boundaries
- Adding beginner-friendly explanations

### AI Module Structure

```txt
ai/
├── prompt_builder.py
├── llm_client.py
├── report_generator.py
├── analysis_service.py
└── schemas.py
```

## 13. Report Generation Flow

```txt
User clicks "Request Report"
    ↓
Frontend sends request to Backend
    ↓
Backend loads holdings / watchlist from database
    ↓
Backend fetches market data and news
    ↓
Backend builds structured AI prompt
    ↓
Backend calls LLM API
    ↓
Backend receives AI-generated report
    ↓
Backend stores report in PostgreSQL
    ↓
Backend returns report to Frontend
    ↓
Frontend displays report
```

## 14. Chat Flow

```txt
User sends chat message
    ↓
Frontend sends message to Backend
    ↓
Backend checks whether the question is investment-related
    ↓
Backend loads relevant context if needed
    ├── Holdings
    ├── Watchlist
    ├── Recent reports
    ├── Market data
    └── News
    ↓
Backend builds chat prompt
    ↓
Backend calls LLM API
    ↓
Backend stores message and response
    ↓
Backend returns response to Frontend
```

## 15. Local Development Architecture

The MVP should run locally using Docker.

Recommended local services:

```txt
docker-compose
    ├── frontend
    ├── backend
    └── postgres
```

Optional future services:

```txt
    ├── redis
    ├── worker
    └── scheduler
```

For the MVP, Redis, background workers, and schedulers are not required unless needed later.

## 16. Deployment Direction

The MVP runs locally.

Future versions may be deployed as a website.

The architecture should prepare for future deployment by using:

- Environment variables
- Docker containers
- Clear frontend/backend separation
- Database migrations
- API-based communication
- No hardcoded local paths
- No secrets committed to Git

Possible future deployment targets:

- Frontend: Vercel, Netlify, or static hosting
- Backend: Render, Fly.io, Railway, cloud VM, or container service
- Database: managed PostgreSQL
- Domain name: custom domain later

The MVP does not need production deployment, but the codebase should not block it.

## 17. Security Considerations

The MVP should protect API keys and user data.

Basic rules:

- Store API keys in environment variables.
- Do not expose LLM or market data API keys to the frontend.
- Do not commit `.env` files.
- Provide `.env.example`.
- Backend validates incoming requests.
- Chat should be limited to investment-related use cases.
- Generated suggestions should include financial advice boundaries.

Future versions may add:

- User authentication
- Session management
- Role-based access control
- Rate limiting
- Audit logs
- Secure secret storage

## 18. Why Not Full Microservices in MVP

The project should not start with full microservices.

Reasons:

- More deployment complexity
- More networking complexity
- More debugging difficulty
- More authentication and logging work
- Slower MVP progress
- Unnecessary for a single-user local app

A modular monolith gives most of the learning value while keeping the project buildable.

## 19. Architecture Decision Summary

Current architecture decisions:

- Use React + TypeScript for frontend.
- Use FastAPI + Python for backend.
- Use PostgreSQL as the database.
- Use Docker and docker-compose for local development.
- Use modular monolith architecture.
- Keep frontend and backend separated.
- Keep market data provider layer replaceable.
- Keep AI logic inside backend for MVP.
- Design AI module so it can become a separate service later.
- Design the system for future web deployment, but keep MVP local-first.