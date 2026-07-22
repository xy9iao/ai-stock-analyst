> **v0 Outcome (2026-07-02).** yfinance served all of v0 behind the three provider Protocols (market / news / financials) — the §13–14 provider bake-off (FMP vs Finnhub) never happened; the abstraction made it unnecessary. Caching landed as cache-aside in Postgres (quotes ~2 min, news ~15 min, financials ~1 day). News context shipped headline-level, no URLs in prompts, per §8.
>
> **v1 planned (2026-07-03):** Phase 14 supersedes §8's "no citations" stance — reports gain source-backed citations via hybrid RAG (pgvector + FTS→BM25, RRF); ingestion reuses the existing fetch layer. Scope in `docs/roadmap.md`; on conflict, the roadmap wins.
>
> **v1 shipped (2026-07-21).** Delivered: news bodies ingested via `trafilatura` (reusing the fetch layer) → chunked → OpenAI `text-embedding-3-small` → pgvector; retrieval is hybrid (pgvector cosine + Postgres FTS rescored with `rank_bm25`, RRF-fused); reports now carry clickable source citations. Corpus is seeded per-ticker via `POST /api/admin/ingest` (see `docs/guides/deployment.md` Step 6).

## 1. Purpose

This document defines the MVP data source strategy for AI Stock Analyst.

The system needs market data, news data, company data, and earnings-related data to generate useful AI-powered investment analysis.

The MVP should prioritize free or low-cost data sources, while keeping the data provider layer modular so the project can switch providers later.

## 2. MVP Market Coverage

The MVP will focus on the U.S. stock market.

Primary market focus:

- U.S.-listed stocks
- S&P 500
- Nasdaq
- Major technology companies
- Active and high-volume stocks
- User holdings
- User watchlist

Secondary future interests:

- Resource companies
- Gold-related equities or ETFs
- Silver-related equities or ETFs
- Broader macro-sensitive assets

The MVP should not support global markets, options, futures, crypto, forex, or complex multi-asset analysis.

## 3. Data Categories

The MVP needs the following data categories:

1. Market index data
2. Stock quote data
3. Historical price and volume data
4. Company news
5. Macro market news
6. Earnings / financial statement data
7. Company profile data
8. User-provided holdings and watchlist data

## 4. Market Index Data

The system should fetch basic data for major indexes.

Required indexes:

- S&P 500
- Nasdaq Composite or Nasdaq 100

Useful fields:

- Current price or index level
- Daily change
- Daily percentage change
- Historical price data
- Volume if available

Purpose:

- Explain overall market direction
- Provide context for stock-specific movement
- Help the AI understand whether a stock moved with or against the market

## 5. Stock Quote Data

The system should fetch quote data for holdings and watchlist stocks.

Required fields:

- Ticker
- Current price
- Daily price change
- Daily percentage change
- Open price
- Previous close
- Day high
- Day low
- Volume if available
- Latest update timestamp if available

Purpose:

- Display current stock state in Holdings and Watchlist
- Calculate portfolio market value
- Calculate unrealized gain or loss
- Provide context for AI reports

## 6. Historical Price and Volume Data

The MVP should support simple chart data.

Required chart ranges:

- 1 day
- 1 week
- 1 month
- 1 year

Required chart fields:

- Timestamp or date
- Open price
- High price
- Low price
- Close price
- Volume

The UI should display both price and volume when possible.

Purpose:

- Help users visually understand recent movement
- Help AI analysis reference recent trend context
- Prepare for future chart-based analysis

The MVP does not need advanced technical indicators.

Future versions may add:

- Moving averages
- RSI
- MACD
- Bollinger Bands
- Support and resistance
- Trend detection
- Chart pattern summary

## 7. News Data

The MVP should include both macro news and company news.

### 7.1 Macro News

Macro news should cover market-moving topics such as:

- Federal Reserve decisions
- Inflation data
- Interest rates
- Employment data
- GDP data
- Treasury yields
- Market-wide risk sentiment
- Major geopolitical events that affect U.S. markets
- Broad technology sector news

Purpose:

- Explain S&P 500 and Nasdaq movement
- Help users understand market direction
- Provide context for portfolio-level analysis

### 7.2 Company News

Company news should cover:

- User holdings
- Watchlist companies
- Major technology companies
- Active market names

Purpose:

- Explain stock-specific movement
- Identify risks and opportunities
- Support single-stock analysis
- Support holdings and watchlist reports

## 8. News Token Strategy

The MVP should avoid sending full news articles to the LLM.

To reduce token usage, the system should send compact news summaries or structured metadata.

Preferred MVP news context:

- Headline
- Source name if available
- Published date
- Short description or summary if available
- Related ticker
- URL stored in database if available

The MVP does not need to include article links in the AI prompt.

The system may store links in the database for future reference, but should avoid sending unnecessary links to the LLM to save tokens.

Future versions may support source-backed citations in reports.

## 9. Earnings and Financial Data

The MVP should support latest earnings or financial statement data when available.

The goal is not to build a full financial modeling system in the first version.

Instead, the system should fetch the latest financial data and pass a compact version to the AI.

Useful fields may include:

- Latest revenue
- Revenue growth if available
- EPS
- EPS growth if available
- Net income
- Gross margin
- Operating margin
- Free cash flow if available
- Guidance if available
- Latest earnings date
- Next earnings date if available

Purpose:

- Help the AI understand company fundamentals
- Support long-term investment analysis
- Help users understand whether recent performance supports or weakens the investment thesis

## 10. Earnings Token Strategy

The MVP should not send full financial statements to the LLM unless necessary.

The backend should prepare a compact earnings snapshot.

Example earnings snapshot:

```txt
Ticker: NVDA
Latest quarter: 2026 Q1
Revenue: ...
Revenue YoY growth: ...
EPS: ...
EPS surprise: ...
Gross margin: ...
Operating margin: ...
Key management guidance: ...
Next earnings date: ...
```

If full earnings call transcripts are added later, they should be summarized before being included in report prompts.

## 11. Company Profile Data

The MVP should fetch simple company profile data.

Useful fields:

- Company name
- Ticker
- Sector
- Industry
- Market cap
- Exchange
- Description if available

Purpose:

- Display readable company information
- Help beginner users understand what the company does
- Give the AI basic company context

## 12. User Data

The user manually enters holdings and watchlist data.

### Holdings Data

Required:

- Ticker
- Shares
- Average cost

Optional:

- Company name
- Sector
- Notes
- Target allocation
- Investment thesis

### Watchlist Data

Required:

- Ticker

Optional:

- Company name
- Sector
- Reason to watch
- Notes

User data should be stored in PostgreSQL.

## 13. Candidate Data Providers

The MVP should evaluate the following providers.

### 13.1 Financial Modeling Prep

Financial Modeling Prep is a strong candidate because it provides:

- Stock prices
- Historical prices
- Market news
- Fundamentals
- Company profile data
- Index data

Possible use cases:

- Quote data
- Historical price and volume
- Company profile
- Financial statements
- Market news
- Index data

Pros:

- Broad coverage
- Good fit for financial app development
- Has many relevant endpoints
- Useful for both market data and fundamentals

Cons:

- Requires API key
- Free tier may have limits
- Some features may require paid plans
- Licensing should be reviewed before public deployment

### 13.2 Finnhub

Finnhub is another strong candidate because it provides:

- Real-time stock data
- Company fundamentals
- Economic data
- Company news
- Market data APIs

Possible use cases:

- Quote data
- Company news
- Fundamentals
- Economic data
- Earnings-related data

Pros:

- Free API access available
- Strong stock API coverage
- Useful for market and company data
- Good candidate for MVP

Cons:

- Requires API key
- Free plan has rate limits
- Some advanced data may require paid plans
- Licensing should be reviewed before public deployment

### 13.3 yfinance

yfinance can be used as a prototype fallback.

Possible use cases:

- Historical price data
- Simple quote data
- Local testing
- Fast prototype development

Pros:

- Easy to use in Python
- No formal API key needed
- Good for early local experiments
- Returns data in convenient formats

Cons:

- Not an official market data API
- Can be rate limited or blocked
- May break if Yahoo Finance changes endpoints
- Not ideal as the only long-term data source

### 13.4 Alpha Vantage

Alpha Vantage may be considered later.

Possible use cases:

- Time series data
- Technical indicators
- Company overview
- News and sentiment

Pros:

- Well-known API
- Free tier exists
- Useful educational and hobbyist option
- Has many documented endpoints

Cons:

- Free tier may be too limited for repeated development usage
- Some real-time or advanced features may require paid plans
- May not be the best one-stop source for this MVP

## 14. Recommended MVP Provider Strategy

The recommended MVP strategy is:

```txt
Primary provider candidate:
- Financial Modeling Prep or Finnhub

Prototype fallback:
- yfinance

Optional later provider:
- Alpha Vantage
```

The project should start by testing Financial Modeling Prep and Finnhub free tiers.

The final MVP provider should be selected based on:

- Free tier limits
- Data coverage
- Ease of use
- Historical price support
- Volume support
- News support
- Earnings / financial data support
- Documentation quality
- Reliability during development

## 15. Provider Abstraction Requirement

The backend must not hardcode all business logic to one data provider.

The market data module should define a provider interface.

Example:

```txt
MarketDataProvider
    get_quote(ticker)
    get_price_history(ticker, range)
    get_company_profile(ticker)
    get_market_index(index)
```

The news module should define a provider interface.

Example:

```txt
NewsProvider
    get_company_news(ticker, from_date, to_date)
    get_macro_news(topic, from_date, to_date)
```

The financial data module should define a provider interface.

Example:

```txt
FinancialDataProvider
    get_latest_financials(ticker)
    get_earnings_calendar(ticker)
    get_company_profile(ticker)
```

This allows future provider replacement without rewriting report generation logic.

## 16. Data Caching Strategy

The MVP should cache market data where useful.

Reasons:

- Reduce API calls
- Avoid hitting free tier limits
- Improve page load speed
- Prevent repeated calls when the user refreshes pages

Possible cache rules:

- Quote data: short cache window
- Historical chart data: longer cache window
- Company profile: long cache window
- Financial statement data: long cache window
- News data: medium cache window

Exact cache durations should be decided after choosing the provider.

The MVP may store cached data in PostgreSQL.

Future versions may use Redis if needed.

## 17. LLM Context Packaging

The backend should not send raw API responses directly to the LLM.

Instead, the backend should transform raw data into compact structured context.

Example context package:

```json
{
  "market_summary": {
    "sp500_change_pct": "...",
    "nasdaq_change_pct": "...",
    "macro_headlines": []
  },
  "holdings": [
    {
      "ticker": "NVDA",
      "shares": "...",
      "average_cost": "...",
      "current_price": "...",
      "price_change_pct": "...",
      "unrealized_pl_pct": "...",
      "recent_news": [],
      "latest_financial_snapshot": {}
    }
  ],
  "watchlist": [
    {
      "ticker": "AMD",
      "current_price": "...",
      "price_change_pct": "...",
      "recent_news": [],
      "latest_financial_snapshot": {}
    }
  ]
}
```

This improves:

- Token efficiency
- Prompt quality
- Report consistency
- Cost control

## 18. MVP Data Flow

```txt
User requests report
    ↓
Backend loads holdings and watchlist from PostgreSQL
    ↓
Backend checks cache
    ↓
Backend fetches missing or stale market data
    ↓
Backend fetches relevant news
    ↓
Backend fetches latest financial / earnings snapshot
    ↓
Backend normalizes provider responses
    ↓
Backend builds compact LLM context
    ↓
Backend sends structured prompt to LLM
    ↓
AI generates report
    ↓
Backend stores report in PostgreSQL
    ↓
Frontend displays report
```

## 19. Data Quality Considerations

The MVP should handle imperfect data.

Possible issues:

- Missing ticker
- Invalid ticker
- API rate limit
- Delayed price data
- Missing financial data
- Missing news
- Provider downtime
- Inconsistent field names across providers
- Different market holiday behavior

The backend should return clear error messages when data is missing.

The AI should state uncertainty when data is incomplete.

## 20. Token Cost Considerations

The MVP should reduce token usage by:

- Sending only relevant holdings and watchlist data
- Sending compact news summaries instead of full articles
- Sending latest financial snapshot instead of full statements
- Limiting number of news items per ticker
- Limiting macro news items
- Avoiding unnecessary URLs in prompts
- Reusing cached reports where appropriate

The goal is to make the app useful without excessive LLM cost.

## 21. Future Data Source Expansion

Future versions may add:

- SEC filings
- Earnings call transcripts
- Analyst ratings
- Insider trading data
- Institutional ownership
- ETF holdings
- Economic calendar
- Treasury yields
- Commodity prices
- Gold and silver data
- Social sentiment
- Reddit or X sentiment
- Alternative data
- Real-time streaming quotes
- Paid professional market data APIs

These are not part of the MVP.