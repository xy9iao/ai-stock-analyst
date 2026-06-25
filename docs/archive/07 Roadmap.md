## 1. Purpose

This document defines the phased development roadmap for AI Stock Analyst.

The roadmap is designed around the current development situation:

- Current date: 2026-06-21
- Planning documents are stored in Obsidian
- Implementation is happening in the separate `ai-stock-analyst` development repository
- Phase 0 planning is complete
- Phase 1 repository and development environment setup is complete
- Phase 2 backend and database foundation is complete
- Current active phase: Phase 3 Holdings and Watchlist CRUD
- MVP will be local-first
- Final README and public-facing repo documentation will be polished after the MVP is working

The roadmap uses phases instead of fixed weekly deadlines because available development time may vary.

## Current Progress

Current active phase:

**Phase 3: Holdings and Watchlist Modules**

Completed phases:

- Phase 0: Planning and Design
- Phase 1: Repository and Development Environment Setup
- Phase 2: Backend and Database Foundation

Current Phase 3 focus:

- Manual Holdings CRUD
- Manual Watchlist CRUD
- Backend repository/service/router structure
- Pydantic request/response schemas
- Backend CRUD tests
- Frontend Holdings page
- Frontend Watchlist page
- Frontend API client functions
- Basic forms and tables

Do not start market data, AI reports, or chat during Phase 3 unless intentionally re-scoped later.

## 2. Development Capacity

Expected available time:

- Weekdays: 1 to 2 hours per day
- Weekend: around 1 full day per weekend

This means the project should be planned as a gradual build, not a rushed sprint.

The roadmap should prioritize steady progress and clear milestones.

## 3. Development Strategy

The recommended strategy is:

1. Finish Obsidian planning documents first.
2. Use the documents as context for AI coding assistance.
3. Build the project as a modular full-stack web application.
4. Start with backend, database, and service boundaries.
5. Add frontend pages after core data models and APIs are clear.
6. Add AI analysis after data flow works.
7. Polish README and public repo documentation after MVP completion.

The project should avoid jumping directly into UI coding without a clear backend and data structure.

## 4. AI Tool Usage Strategy

Before upgrading to a higher-tier AI plan, the project can still make useful progress.

### Before late June

Focus on:

- Obsidian planning
- Architecture design
- Data model design
- API design
- Prompt design
- Repo structure
- Basic backend skeleton
- Basic database setup
- Docker setup

These tasks can be done with normal AI assistance and do not require heavy coding quota.

### After getting stronger AI coding capacity

Focus on:

- Generating implementation code
- Refactoring modules
- Writing tests
- Debugging
- Improving frontend UI
- Building data provider integrations
- Building AI report generation
- Preparing README and demo materials

This reduces migration risk because the important project context will already be documented in Obsidian.

## 5. Phase 0: Planning and Design

### Goal

Create a clear project brain in Obsidian before writing major code.

### Deliverables

- `00 Project Charter.md`
- `01 Vision.md`
- `02 Requirements.md`
- `03 User Stories.md`
- `04 Architecture.md`
- `05 Data Sources.md`
- `06 AI Design.md`
- `07 Roadmap.md`
- `08 Decisions.md`
- Optional: `09 Open Questions.md`

### Success Criteria

Phase 0 is complete when:

- The project goal is clear.
- MVP scope is clear.
- Main pages are defined.
- Architecture is defined.
- Data source strategy is defined.
- AI behavior is defined.
- Major technical decisions are recorded.

## 6. Phase 1: Repository and Development Environment Setup

### Goal

Create the initial project repository and local development environment.

### Tasks

- Create GitHub repository
- Add base folder structure
- Add `.gitignore`
- Add `.env.example`
- Add frontend folder
- Add backend folder
- Add docker-compose setup
- Add PostgreSQL container
- Add backend Dockerfile
- Add frontend Dockerfile if needed
- Add basic README draft
- Confirm frontend and backend can run locally

### Suggested Repo Structure

```txt
ai-stock-analyst/
├── frontend/
├── backend/
├── docs/
├── prompts/
├── scripts/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

### Success Criteria

Phase 1 is complete when:

- The repo exists.
- Docker can start PostgreSQL.
- Backend can start locally.
- Frontend can start locally.
- Frontend can call a backend health check endpoint.

## 7. Phase 2: Backend and Database Foundation

### Goal

Build the backend foundation before implementing complex features.

### Tasks

- Set up FastAPI project structure
- Set up PostgreSQL connection
- Set up SQLAlchemy
- Set up Alembic migrations
- Create core config module
- Create error handling structure
- Create basic logging setup
- Create health check endpoint
- Create initial database models

### Initial Database Tables

- `holdings`
- `watchlist_items`
- `reports`
- `chat_sessions`
- `chat_messages`
- `stock_notes`
- `market_data_cache`
- `settings`

### Success Criteria

Phase 2 is complete when:

- Backend connects to PostgreSQL.
- Database migrations work.
- Basic tables can be created.
- Health check endpoint works.
- Project structure follows modular monolith design.

## 8. Phase 3: Holdings and Watchlist Modules

### Goal

Build the core user data modules.

### Tasks

- Implement Holdings module
- Implement Watchlist module
- Add CRUD APIs for holdings
- Add CRUD APIs for watchlist items
- Add validation for ticker, shares, and average cost
- Add Pydantic request and response schemas
- Add repository/service/router structure for each module
- Add backend tests for CRUD, validation, not found, and delete behavior
- Add frontend pages for Holdings and Watchlist
- Add frontend API client functions
- Add forms for manual data entry
- Add tables for displaying records
- Add loading, error, and empty states

Phase 3 should not include:

- Market data provider integration
- Current price fetching
- Real stock charts
- AI action labels
- AI reports
- Chat

Alembic already exists from Phase 2. Phase 3 should only add a migration if the existing holdings or watchlist schema needs to change.

### Holdings Required Fields

- `ticker`
- `shares`
- `average_cost`

### Holdings Optional Fields

- `company_name`
- `sector`
- `notes`
- `target_allocation`
- `investment_thesis`

### Watchlist Fields

- `ticker`
- `company_name`
- `sector`
- `reason_to_watch`
- `notes`

### Success Criteria

Phase 3 is complete when:

- User can manually add holdings.
- User can manually edit holdings.
- User can manually delete holdings.
- User can manually add watchlist items.
- User can manually edit watchlist items.
- User can manually delete watchlist items.
- Data persists in PostgreSQL.
- Frontend displays holdings and watchlist records.
- Backend CRUD tests pass.
- Frontend can create, edit, and delete records through the backend API.
- Phase 3 remains focused on manual holdings/watchlist management without market data or AI features.

## 9. Phase 4: Market Data Integration

### Goal

Fetch and display market data for holdings and watchlist stocks.

### Tasks

- Create market data provider interface
- Test free data providers
- Implement first provider
- Implement fallback provider if needed
- Fetch current price
- Fetch daily price change
- Fetch daily percentage change
- Fetch historical price and volume
- Cache market data to reduce API calls
- Display price and percentage change in frontend
- Display basic charts

### Chart Ranges

- 1 day
- 1 week
- 1 month
- 1 year

### Success Criteria

Phase 4 is complete when:

- Holdings show current price.
- Holdings show percentage change.
- Watchlist shows current price.
- Watchlist shows percentage change.
- Stock detail page can show price and volume chart.
- Backend has a provider abstraction layer.
- API rate limits are considered.

## 10. Phase 5: News and Financial Data Integration

### Goal

Add market news, company news, and latest financial snapshot data.

### Tasks

- Create news provider interface
- Fetch company news for holdings and watchlist
- Fetch macro news related to S&P 500 and Nasdaq
- Fetch latest earnings or financial snapshot when available
- Store or cache useful news metadata
- Prepare compact news context for AI
- Prepare compact financial snapshot for AI

### MVP Token Strategy

The backend should not send full articles or full financial statements to the LLM.

It should send compact structured context.

### Success Criteria

Phase 5 is complete when:

- Backend can fetch company news for a ticker.
- Backend can fetch macro news.
- Backend can fetch or prepare latest financial snapshot.
- Backend can package news and financial data into compact AI context.

## 11. Phase 6: AI Report Generation

### Goal

Implement AI-powered report generation.

### Tasks

- Create AI module
- Create LLM client
- Create prompt builder
- Create report generator
- Implement Markdown report output
- Implement overall market + portfolio report
- Implement holdings analysis report
- Implement watchlist opportunity report
- Implement single-stock analysis report
- Store generated reports in database
- Display reports in frontend

### Report Style

Reports should:

- Start with a direct conclusion
- Give suggested actions for important stocks only
- Separate Long-Term View and Swing View
- Use beginner-friendly explanations
- Include confidence level when giving action-oriented suggestions
- Avoid guaranteed financial advice language

### Success Criteria

Phase 6 is complete when:

- User can request a report from Dashboard.
- User can request holdings analysis.
- User can request watchlist analysis.
- User can request single-stock analysis.
- Report is displayed in Markdown.
- Report is stored in PostgreSQL.

## 12. Phase 7: Chat Module

### Goal

Add an investment-focused chat assistant.

### Tasks

- Create chat backend module
- Create chat sessions and messages tables
- Create chat UI page
- Add investment-related scope control
- Inject holdings/watchlist/report context when useful
- Store chat history
- Support follow-up questions

### Supported Chat Topics

- Stock knowledge
- Holdings adjustment
- Watchlist adjustment
- Market news
- Report follow-up
- Beginner investment education
- Prompt writing for other financial models

### Success Criteria

Phase 7 is complete when:

- User can send investment-related messages.
- Chatbot can answer with relevant context.
- Chatbot can use holdings/watchlist data when needed.
- Chat history is stored.
- Chat avoids unrelated general-purpose conversation.

## 13. Phase 8: Export and Logging

### Goal

Allow the user to save reports and conversations.

### Tasks

- Add export button for generated reports
- Add export button for chat history
- Support Markdown export
- Optionally support plain text export
- Add daily log concept if needed

### Preferred MVP Export Format

- Markdown

### Success Criteria

Phase 8 is complete when:

- User can export at least one report as Markdown.
- User can export chat history or daily log.
- Exported output works well with Obsidian.

## 14. Phase 9: UI Polish and Beginner Experience

### Goal

Improve usability for beginner investors.

### Tasks

- Improve Dashboard layout
- Improve Holdings table
- Improve Watchlist table
- Improve Stock Detail page
- Add action label UI
- Add colors for recommendation strength
- Add loading states
- Add error states
- Add empty states
- Add beginner-friendly tooltips if needed

### Success Criteria

Phase 9 is complete when:

- User can understand the app without reading documentation.
- Main actions are easy to find.
- AI recommendations are visually clear.
- The app feels like a coherent product rather than a collection of pages.

## 15. Phase 10: Testing and Quality

### Goal

Make the project more reliable and maintainable.

### Tasks

- Add backend unit tests
- Add API tests
- Add basic frontend tests if needed
- Test CRUD flows
- Test data provider failure behavior
- Test AI report generation with sample data
- Test Docker setup
- Test environment variable setup

### Success Criteria

Phase 10 is complete when:

- Core backend APIs have tests.
- Main user flows work reliably.
- Docker setup works from a clean checkout.
- Common API errors are handled clearly.

## 16. Phase 11: README and Public Repo Documentation

### Goal

Prepare the project for GitHub and portfolio use.

### Tasks

- Write polished README
- Add project screenshots
- Add architecture diagram
- Add setup instructions
- Add environment variable instructions
- Add API key setup instructions
- Add demo workflow
- Add financial advice disclaimer
- Add future roadmap section
- Add tech stack explanation

### Success Criteria

Phase 11 is complete when:

- A recruiter or developer can understand the project quickly.
- A developer can run the project locally.
- The README explains the product, architecture, and technical value.
- The project can be used as a portfolio project.

## 17. Phase 12: Future Deployment Preparation

### Goal

Prepare the project for future web deployment, but not necessarily deploy during MVP.

### Tasks

- Review production environment variables
- Review API key handling
- Review database migration flow
- Review frontend build process
- Review backend deployment options
- Decide possible hosting providers
- Decide whether user accounts are needed before deployment

### Success Criteria

Phase 12 is complete when:

- The project is structurally ready for deployment.
- Major blockers for future deployment are known.
- The MVP can remain local-first while keeping deployment path open.

## 18. Recommended Build Order

The recommended build order is:

```txt
Planning
    ↓
Repo skeleton
    ↓
Backend + database foundation
    ↓
Holdings + Watchlist CRUD
    ↓
Market data integration
    ↓
News + financial snapshot integration
    ↓
AI report generation
    ↓
Frontend UI polish
    ↓
Chat
    ↓
Export
    ↓
Tests
    ↓
README and demo
```

This order is recommended because the core value of the product depends on data and AI analysis, not just UI.

## 19. MVP Definition

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

## 20. Post-MVP Ideas

After MVP, possible next steps include:

- User accounts
- Public web deployment
- More advanced onboarding
- Investment style profiling
- Better financial data integration
- Earnings call transcript analysis
- SEC filing analysis
- Professional mode
- Alert system
- Email reports
- Subscription features
- More advanced technical analysis
- RAG over past reports and thesis notes
- Agent-based research workflow
