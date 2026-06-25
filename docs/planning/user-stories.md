## 1. Purpose

This document defines the main user stories for the MVP version of AI Stock Analyst.

The goal is to describe how a beginner investor may use the application in real scenarios.

The MVP should support three main user flows:

1. Daily market and holdings check
2. Investment decision support
3. Learning and research through chat

## 2. User Profile

The primary user is a beginner investor.

The user may:

- Know basic stock concepts but lack deeper financial knowledge
- Hold several stocks but not know how to review them systematically
- Have a watchlist but not know when to act
- Want to understand market news without reading many sources manually
- Want direct suggestions first, followed by beginner-friendly explanations
- Want to use AI to reduce emotional or random investing decisions

The product should help the user make more structured and explainable investment decisions.

## 3. Core User Flow 1: Daily Check

### Scenario

The user opens the app to quickly check the current state of their holdings.

### User Story

As a beginner investor, I want to open the app and review my current holdings, so that I can quickly understand whether anything important happened today.

### Flow

1. The user opens the web app.
2. The user goes to the Holdings page.
3. The app displays current holdings, prices, daily changes, and basic charts.
4. The user clicks a button to request a holdings report.
5. The system fetches relevant market data and news.
6. The AI generates a holdings-focused report.
7. The user reads suggested actions and explanations.

### Expected Output

The holdings report should include:

- Current portfolio summary
- Major gainers and losers
- Important news related to holdings
- Explanation of price movement
- Suggested action labels
- Long-term investment view
- Short-term trading view
- Risk notes
- Follow-up questions the user may want to ask

## 4. Core User Flow 2: Investment Decision

### Scenario

The user wants to decide whether to buy, add, hold, reduce, sell, or wait.

### User Story

As a beginner investor, I want to see a combined summary of my holdings and watchlist, so that I can make a better investment decision.

### Flow

1. The user opens the web app.
2. The Dashboard shows a combined overview of holdings and watchlist.
3. The user requests an overall market and portfolio report.
4. The system fetches market index data, holdings data, watchlist data, and relevant news.
5. The AI generates a combined investment report.
6. The report gives action labels and reasoning.
7. The user can open a stock detail page for deeper analysis.
8. The user can continue asking questions in Chat.

### Expected Output

The investment decision report should include:

- Overall market environment
- S&P 500 and Nasdaq summary
- Macro news summary
- Holdings analysis
- Watchlist opportunity analysis
- Suggested action for each important stock
- Portfolio-level risks
- Stocks that require further research
- Possible actions such as buy, add gradually, hold, wait, reduce, sell, or avoid

## 5. Core User Flow 3: Learning and Research

### Scenario

The user wants to learn about stock investing or understand a market event.

### User Story

As a beginner investor, I want to ask investment-related questions in chat, so that I can learn stock market knowledge and understand my investment decisions better.

### Flow

1. The user opens the Chat page.
2. The user asks a question related to stocks, investing, market news, holdings, watchlist, or reports.
3. The chatbot answers directly first.
4. The chatbot explains the reasoning using beginner-friendly terminology.
5. The user can ask follow-up questions.
6. The user can export the conversation if needed.

### Supported Question Types

The Chat page should support:

- Stock knowledge questions
- Holdings adjustment questions
- Watchlist adjustment questions
- Market news questions
- Report follow-up questions
- Beginner investment education
- Prompt-writing help for other financial models

### Example Questions

- What does P/E ratio mean?
- Based on my holdings, should I adjust anything?
- Based on my watchlist, which stocks should I pay attention to?
- What happened in the market today?
- Why did the Nasdaq fall today?
- Why did this stock rise today?
- Help me write a prompt for another financial model.
- Explain this report in simpler terms.
- Should I add gradually or wait for a pullback?
- What are the main risks in my current portfolio?

## 6. Core User Flow 4: Single Stock Analysis

### Scenario

The user wants to understand one specific stock more deeply.

### User Story

As a beginner investor, I want to open a stock detail page and request AI analysis, so that I can understand whether the stock is worth holding, buying, reducing, or watching.

### Flow

1. The user opens a stock from Holdings, Watchlist, or Dashboard.
2. The Stock Detail page displays price, change percentage, chart, notes, and news.
3. The user clicks a button to request analysis.
4. The system fetches relevant stock data and news.
5. The AI generates a single-stock analysis report.
6. The user can continue asking questions in Chat.

### Expected Output

The single-stock analysis should include:

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
- Beginner-friendly explanation

## 7. Core User Flow 5: Manual Data Entry

### Scenario

The user wants to add holdings or watchlist items manually.

### User Story

As a user, I want to manually enter my holdings and watchlist, so that the app can analyze my portfolio and tracked stocks.

### Flow

1. The user opens Holdings or Watchlist.
2. The user clicks Add.
3. The user enters required information.
4. The app saves the record to the local database.
5. The app fetches current market data for the ticker.
6. The stock becomes available for reports and chat context.

### MVP Data Entry Method

The MVP should support manual entry first.

Future versions may support:

- Screenshot import
- CSV import
- Broker export import
- Structured table copy-paste
- Automatic parsing from other apps

## 8. Core User Flow 6: Exporting Logs and Conversations

### Scenario

The user wants to save today's analysis or conversation.

### User Story

As a user, I want to export today's report or chat history, so that I can keep a record of my investment thinking.

### Flow

1. The user generates a report or has a chat conversation.
2. The user clicks an export or download button.
3. The app exports the report or conversation history.
4. The user saves the file locally.

### Exportable Content

The MVP may support exporting:

- Today's report
- Single-stock analysis
- Holdings analysis
- Watchlist analysis
- Chat conversation history

The exact export format can be decided later.

Possible formats include:

- Markdown
- PDF
- Plain text
- JSON

For the MVP, Markdown export is preferred because it is simple and works well with Obsidian.

## 9. AI Response Style

The AI should give direct suggestions first, then explain the reasoning.

The response style should be:

1. Clear conclusion
2. Suggested action
3. Short reasoning
4. Beginner-friendly explanation
5. Risks and uncertainty
6. Follow-up questions or next steps

The AI should avoid overly complex financial language in the MVP.

When financial terms are necessary, the AI should explain them using entry-level terminology.

## 10. Action-Oriented User Stories

### Holdings Adjustment

As a user, I want the AI to review my holdings and suggest adjustments, so that I can decide whether to hold, add, reduce, or sell.

### Watchlist Adjustment

As a user, I want the AI to review my watchlist and identify potential opportunities, so that I can decide which stocks are worth researching further.

### News Understanding

As a user, I want the AI to summarize important market news, so that I can understand what affected the market without reading many articles.

### Beginner Education

As a user, I want the AI to explain stock concepts in simple language, so that I can gradually improve my investment knowledge.

### Prompt Support

As a user, I want the AI to help me write prompts for other financial models, so that I can use external AI tools more effectively.

### Report Export

As a user, I want to download today's report or export my chat history, so that I can keep a personal investment log.

## 11. MVP Acceptance Criteria

The MVP should be considered successful if:

- The user can manually add holdings.
- The user can manually add watchlist items.
- The user can fetch current price and percentage change.
- The user can request a holdings report.
- The user can request a combined market, holdings, and watchlist report.
- The user can request single-stock analysis.
- The user can ask investment-related questions in Chat.
- The AI gives direct suggestions with beginner-friendly explanations.
- The user can open a stock detail page from holdings or watchlist.
- The user can export or download at least one type of report or log.