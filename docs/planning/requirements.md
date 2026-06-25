## 1. Purpose

This document defines the functional and non-functional requirements for the MVP version of AI Stock Analyst.

The MVP should be a local-first web application that helps a beginner investor manage holdings and watchlist stocks, fetch market data, generate AI-powered analysis, and ask investment-related questions.

The first version should focus on stock analysis support, not automated trading.

## 2. MVP Product Scope

The MVP will support:

- Single-user local deployment
- User holdings management
- Watchlist management
- Market data display
- Basic stock chart display
- On-demand AI report generation
- Individual stock analysis
- Portfolio and watchlist analysis
- Investment-related chat assistant
- Local settings for API keys and model configuration

The MVP will not support:

- Multi-user public deployment
- Brokerage account connection
- Real-money trading
- Automatic trade execution
- Options, futures, or crypto analysis
- Advanced quantitative modeling
- Complex backtesting
- Subscription or payment system
- Email report delivery
- Mobile app or desktop app adaptation

## 3. User Type

The MVP is designed for a single local user.

The user may be a beginner investor who:

- Does not fully understand financial markets
- Does not want to manually read large amounts of market news
- Wants simple explanations of market movement
- Wants help understanding current holdings
- Wants to invest more systematically
- May use both long-term investing and occasional swing trading
- Wants AI-generated reasoning before making decisions

Future versions may support multiple accounts and user-specific profiles.

## 4. Main Pages

The MVP should include the following pages:

### 4.1 Dashboard

The Dashboard is the main landing page.

It should provide a quick overview of:

- Major market index movement
- User portfolio summary
- Watchlist summary
- Latest generated report
- Important market or stock alerts
- Quick action buttons for AI analysis

The Dashboard should allow the user to request an overall market and portfolio report.

### 4.2 Holdings

The Holdings page manages stocks that the user already owns.

It should display:

- Ticker
- Company name
- Number of shares
- Average cost
- Current price
- Price change
- Percentage change
- Market value
- Unrealized profit or loss
- Basic chart preview
- AI action label
- Button to request holdings analysis

The Holdings page should focus on portfolio-aware analysis.

### 4.3 Watchlist

The Watchlist page manages stocks that the user wants to track but does not necessarily own.

It should display:

- Ticker
- Company name
- Sector
- Current price
- Price change
- Percentage change
- Basic chart preview
- Reason to watch
- Notes
- AI action label
- Button to request watchlist analysis

The Watchlist page should focus on opportunity discovery and risk monitoring.

### 4.4 Stock Detail

The Stock Detail page shows detailed information for one selected stock.

A user should be able to open this page from Holdings, Watchlist, or Dashboard.

It should display:

- Ticker
- Company name
- Sector
- Current price
- Daily price change
- Percentage change
- Basic chart
- Recent news
- Existing notes
- Investment thesis if available
- Latest AI analysis if available
- Button to request single-stock analysis

The user should be able to request an AI analysis for any individual stock.

### 4.5 Reports

The Reports section stores generated AI reports.

Reports may be generated from:

- Dashboard
- Holdings page
- Watchlist page
- Stock Detail page

The MVP does not need an advanced report management system, but it should keep recent reports so the user can review previous analysis.

Report types may include:

- Overall Market + Portfolio Report
- Holdings Analysis Report
- Watchlist Opportunity Report
- Single Stock Analysis Report

### 4.6 Chat

The Chat page provides an AI chatbot for investment-related questions.

The chatbot should support questions about:

- Stock market news
- User holdings
- Watchlist stocks
- Market movement
- Macro events
- Generated reports
- Beginner investment education
- Company-specific analysis

The chatbot should reject or redirect questions that are unrelated to investing, stocks, market news, or financial education.

### 4.7 Settings

The Settings page stores local configuration.

It may include:

- Market data API key
- News API key
- LLM API key
- Default AI model
- Preferred report style
- Default market focus
- Local database configuration
- Refresh behavior

For the MVP, settings can remain simple.

## 5. Holdings Requirements

The Holdings page should allow the user to create, read, update, and delete holding records.

### 5.1 Required Fields

Each holding should include:

- `ticker`
- `shares`
- `average_cost`

### 5.2 Optional Fields

Each holding may include:

- `company_name`
- `sector`
- `notes`
- `target_allocation`
- `investment_thesis`

### 5.3 Market Data Fields

The system should fetch or calculate:

- `current_price`
- `price_change`
- `price_change_percentage`
- `market_value`
- `unrealized_profit_loss`
- `unrealized_profit_loss_percentage`

### 5.4 Beginner-Friendly Design

The Holdings page should avoid unnecessary complexity.

The MVP should not require the user to enter every transaction manually.

The user only needs to provide basic position information such as ticker, shares, and average cost.

## 6. Watchlist Requirements

The Watchlist page should allow the user to create, read, update, and delete watchlist records.

Each watchlist item should include:

- `ticker`
- `company_name`
- `sector`
- `reason_to_watch`
- `notes`

The system should fetch:

- `current_price`
- `price_change`
- `price_change_percentage`
- basic chart data
- recent news if available

Watchlist items should be analyzed separately from holdings.

The system should not assume that a watchlist stock is owned by the user.

## 7. Chart Requirements

The MVP should display simple stock price charts.

Each stock should support the following time ranges:

- 1 day
- 1 week
- 1 month
- 1 year

The chart does not need to be advanced in the MVP.

The purpose of the chart is to help the user and the AI understand recent price movement.

Future versions may include:

- Technical indicators
- Moving averages
- Volume analysis
- Support and resistance levels
- AI-readable chart snapshots
- Chart pattern explanation

## 8. Data Refresh Requirements

The system should fetch stock price and percentage change data from external APIs.

The refresh rate should depend on the limits of the selected free API plan.

The MVP should avoid excessive API calls.

Possible refresh behavior:

- Manual refresh button
- Refresh when opening a page
- Cache recent market data
- Avoid repeated calls within a short time window

The exact refresh interval should be decided after choosing the final data provider.

## 9. AI Analysis Requirements

The MVP should support AI-generated analysis in multiple contexts.

### 9.1 Overall Market + Portfolio Report

Generated from the Dashboard.

The report should include:

- Overall market summary
- S&P 500 movement
- Nasdaq movement
- Relevant macro news
- Technology sector summary
- Holdings summary
- Watchlist summary
- Major risks
- Suggested actions
- Questions for further research

### 9.2 Holdings Analysis

Generated from the Holdings page.

The report should include:

- Portfolio summary
- Position-level analysis
- Gain/loss explanation
- Risk exposure
- Long-term investment view
- Short-term trading view
- Suggested actions

### 9.3 Watchlist Opportunity Analysis

Generated from the Watchlist page.

The report should include:

- Watchlist summary
- Important watchlist news
- Potential opportunities
- Risk factors
- Suggested stocks to research further
- Entry timing considerations

### 9.4 Single Stock Analysis

Generated from the Stock Detail page.

The report should include:

- Company summary
- Recent price movement
- Recent news
- Bullish factors
- Bearish factors
- Long-term investment view
- Short-term trading view
- Suggested action
- Confidence level
- Risk level

## 10. AI Action Labels

The system should generate clear action labels.

Supported action labels:

- `Strong Buy`
- `Buy`
- `Add Gradually`
- `Hold`
- `Wait`
- `Reduce`
- `Sell`
- `Avoid`

Each action label should include:

- Reasoning
- Confidence level
- Risk level
- Suggested strategy

Supported strategy examples:

- Long-term DCA
- Hold and monitor
- Add on pullback
- Wait for better entry
- Reduce risk exposure
- Research further
- Short-term swing only
- Avoid for now

The UI should visually distinguish action labels using text and color.

The final color system should be decided during UI design.

## 11. Recommendation Boundary

The system may provide investment suggestions, but every suggestion must be presented as AI-generated analysis support.

The product should not claim to guarantee profit.

The system should avoid presenting analysis as absolute financial advice.

The user remains responsible for final investment decisions.

## 12. Chat Requirements

The Chat page should connect to an LLM API.

The chatbot should only answer questions related to:

- Investing
- Stocks
- Market news
- User holdings
- Watchlist
- Macro events
- Company analysis
- Generated reports
- Beginner financial education

The chatbot should not behave as a general-purpose chatbot.

The chatbot should use available user data when relevant, such as:

- Holdings
- Watchlist
- Recent reports
- Recent market data
- Recent news

Example supported questions:

- Why did NVDA drop today?
- Should I add more to my current holdings?
- What happened to the Nasdaq today?
- Which watchlist stock needs attention?
- What does this macro news mean for tech stocks?
- Explain this report in simpler terms.

## 13. Data Source Requirements

The MVP should use free or low-cost market data sources when possible.

The preferred approach is:

1. Start with a free or easy-to-use data source for prototype development.
2. Use a more formal market data API if the free prototype source is not reliable enough.
3. Keep the data provider layer modular so the project can switch providers later.

Possible data source strategy:

- Prototype fallback: `yfinance`
- Formal free API candidate: `Finnhub`
- Formal free API candidate: `Financial Modeling Prep`

The MVP should avoid being tightly coupled to one provider.

A data provider abstraction should be considered in backend design.

## 14. Local Deployment Requirements

The MVP should be designed for local deployment.

The system should run on the developer's machine.

It should include:

- Frontend application
- Backend API
- Local database
- Environment variable configuration
- API key configuration

A public website, domain name, subscription system, and multi-user production deployment are future features.

## 15. Database Requirements

The MVP should include a database.

The database should store:

- Holdings
- Watchlist items
- Generated reports
- User settings
- Stock notes
- Investment thesis
- Cached market data if needed

The first version only needs one local user.

A future version may support multiple user accounts.

## 16. Non-Functional Requirements

The MVP should be:

- Easy to run locally
- Simple enough for a beginner investor to use
- Clear in UI and explanation
- Modular enough to replace data providers later
- Safe about financial advice boundaries
- Designed for future account support
- Designed for future public web deployment

## 17. Future Requirements

Future versions may include:

- Multi-user account system
- Public website deployment
- Domain name
- User onboarding flow
- Investment style questionnaire
- Risk tolerance profile
- Email report system
- Subscription features
- Professional mode
- More advanced charts
- Technical indicators
- Earnings report analysis
- SEC filing analysis
- Portfolio allocation analysis
- Backtesting
- Alerts and notifications
- More advanced AI memory