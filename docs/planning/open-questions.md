## 1. Purpose

This document records unresolved questions for the AI Stock Analyst project.

Not every decision should be made during the planning stage. Some decisions should be delayed until implementation, testing, or provider research gives more information.

This note helps keep track of important open questions so they are not forgotten.

---

## 2. Data Source Questions

### Q1: Which market data provider should be used first?

Current candidates:

- Financial Modeling Prep
- Finnhub
- yfinance as fallback or prototype provider
- Alpha Vantage as later option

Need to evaluate:

- Free tier limits
- Quote data quality
- Historical price support
- Volume support
- News support
- Earnings and financial data support
- Documentation quality
- Reliability
- Ease of Python integration

### Q2: Should yfinance be used in the first prototype?

yfinance is easy to use, but it is not a formal market data API.

Possible approach:

- Use yfinance only for local prototype testing
- Use Finnhub or Financial Modeling Prep for the more formal MVP version

### Q3: How often should market data refresh?

Possible options:

- Manual refresh only
- Refresh when opening a page
- Cache quote data for a short time
- Cache chart data for a longer time

This should depend on API rate limits.

### Q4: How much news should be sent to the LLM?

Current direction:

- Do not send full articles
- Send compact headline-level context
- Avoid URLs in prompts to save tokens

Need to decide:

- Maximum number of macro news items
- Maximum number of company news items per ticker
- Whether to pre-rank news before sending to AI

---

## 3. Financial Data Questions

### Q5: What financial snapshot fields should be included in MVP?

Possible fields:

- Revenue
- Revenue growth
- EPS
- EPS surprise
- Net income
- Gross margin
- Operating margin
- Free cash flow
- Latest earnings date
- Next earnings date

Need to decide based on provider availability.

### Q6: Should the MVP include earnings call transcripts?

Current direction:

- Not part of MVP
- Possible future feature

Need to decide later whether transcript analysis is worth the cost and complexity.

---

## 4. Frontend and UI Questions

### Q7: Which UI component library should be used?

Possible options:

- Tailwind CSS
- shadcn/ui
- Material UI
- Ant Design
- Plain CSS first

Need to decide based on desired style and development speed.

### Q8: Which charting library should be used?

Possible options:

- Recharts
- Lightweight Charts
- ECharts
- Chart.js

Need to support:

- Price line or candlestick
- Volume
- 1 day / 1 week / 1 month / 1 year ranges

### Q9: Should Reports be a main navigation page?

Current direction:

Reports may not need to be a primary page.

They may appear as:

- Recent Reports on Dashboard
- Latest Analysis on Stock Detail
- Optional Report History page

Need to decide during UI design.

### Q10: How should action labels be displayed?

Supported labels:

- Strong Buy
- Buy
- Add Gradually
- Hold
- Wait
- Reduce
- Sell
- Avoid

Need to decide:

- Color mapping
- Icon usage
- Confidence display
- Risk display
- Whether action labels should appear in tables

---

## 5. Backend and Architecture Questions

### Q11: Should the backend use SQLAlchemy directly or SQLModel?

Current direction:

- SQLAlchemy + Pydantic + Alembic

Need to confirm during backend setup.

### Q12: Should the backend use async database access?

FastAPI supports async patterns, but async database setup adds complexity.

Need to decide:

- Synchronous SQLAlchemy first
- Async SQLAlchemy from the beginning

### Q13: Should Redis be added?

Current direction:

- Not needed for MVP

Possible future uses:

- Caching market data
- Background jobs
- Rate limiting
- Session storage

Need to decide only if PostgreSQL caching is not enough.

### Q14: Should report generation run synchronously or as a background job?

MVP direction:

- Synchronous request-response first

Future direction:

- Background job for longer reports

Need to decide if report generation becomes slow.

---

## 6. AI and Prompting Questions

### Q15: Should reports be stored only as Markdown or also as structured JSON?

MVP direction:

- Store Markdown report output

Future possibility:

- Store structured JSON for better UI rendering
- Render JSON into cards, tables, and sections

Need to decide after first report implementation.

### Q16: Should RAG be added?

Current direction:

- No complex RAG in MVP
- Use simple context injection first

RAG may be useful later for:

- Past reports
- Chat history
- Company thesis notes
- SEC filings
- Earnings transcripts

Need to decide after the MVP chat/report system works.

### Q17: Should agent workflows be added?

Current direction:

- No agent workflow in MVP

Agent workflow may be useful later for:

- Multi-step research
- Comparing multiple stocks
- Finding relevant news automatically
- Generating deep investment memos

Need to decide after the simpler AI system is stable.

### Q18: Which LLM provider should be used?

Possible options:

- OpenAI API
- OpenRouter
- Anthropic API
- Local models

Need to evaluate:

- Cost
- Quality
- Speed
- Tool calling support
- JSON reliability if needed later
- Context window
- Ease of integration

---

## 7. Product Questions

### Q19: Should the MVP include user accounts?

Current decision:

- No user accounts in MVP
- Single-user local-first app

Future possibility:

- User accounts before public deployment

Need to decide before turning the app into a public website.

### Q20: Should the app include onboarding?

Current direction:

- Not in MVP

Future onboarding may ask:

- Investment goal
- Risk tolerance
- Investment time horizon
- Preferred sectors
- Long-term vs short-term preference
- Beginner vs professional mode

Need to decide before supporting multiple users.

### Q21: Should Beginner Mode and Professional Mode be separate UI modes?

Current direction:

- MVP focuses on Beginner Mode only

Future direction:

- Add Professional Mode with deeper charts, metrics, and advanced analysis

Need to decide after the MVP is usable.

### Q22: Should the product support Chinese or bilingual output?

Current decision:

- MVP supports English only

Future possibility:

- Chinese or bilingual support

Need to decide based on users.

---

## 8. Export and Logging Questions

### Q23: What export formats should be supported?

MVP direction:

- Markdown export

Future options:

- PDF
- Plain text
- JSON
- Obsidian direct export

Need to decide after MVP report generation works.

### Q24: Should the app support a daily investment log?

Possible idea:

- Export today's report
- Export today's chat history
- Combine report and conversation into one daily log

Need to decide after report and chat are implemented.

---

## 9. Deployment Questions

### Q25: Where should the app be deployed in the future?

Possible frontend hosts:

- Vercel
- Netlify
- Cloudflare Pages

Possible backend hosts:

- Render
- Railway
- Fly.io
- Cloud VM
- Container service

Possible database:

- Managed PostgreSQL

Need to decide after MVP is complete.

### Q26: How should API keys be managed in production?

MVP direction:

- Local `.env`

Future direction:

- Hosted environment secrets
- User-provided API keys
- Centralized paid API keys

Need to decide before public deployment.

---

## 10. Documentation Questions

### Q27: When should the public README be polished?

Current direction:

- After MVP works

README should eventually include:

- Project overview
- Screenshots
- Tech stack
- Architecture diagram
- Setup instructions
- API key setup
- Demo workflow
- Disclaimer
- Roadmap

### Q28: Which Obsidian notes should be converted into repo docs?

Possible repo docs:

- `docs/architecture.md`
- `docs/api.md`
- `docs/data-model.md`
- `docs/development.md`
- `docs/ai-design.md`

Need to decide after implementation starts.

---

## 11. Current Priority

The most important open questions before coding are:

1. Which market data provider to use first
2. Which UI component library to use
3. Which charting library to use
4. Whether to store reports as Markdown only
5. Whether backend database access should be sync or async
6. Which LLM provider to use first

These should be resolved during early implementation.