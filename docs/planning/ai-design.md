> **v0 Outcome (2026-07-02).** Shipped as designed: simple **DB-context injection** (compact context blocks, no raw payloads), every LLM call through the single `modules/ai/llm_client.py` gateway (DeepSeek, OpenAI-compatible), the advice-safety boundary in the system prompt, Markdown reports stored in `reports`. **RAG and agent workflows stayed deferred.**
>
> **v1 planned (2026-07-03):** the deferral is resolved — v1 adds a hand-written tool-use agent loop + routing experiment (Phase 13), local MCP (13.5), hybrid RAG with cited reports (14), and context compression + injection defense (15). Scope lives in `docs/roadmap.md`; architecture decision in `decisions.md` Decision 010. Where this plan conflicts with sketches below, the roadmap wins.
>
> **v1 shipped (2026-07-21).** Delivered as: hand-written agent loop (Phase 13); **routing became a design decision, not an experiment** (Decision 011 — closed data needs → pipeline, open-ended → agent, chat stays non-agentic); hybrid RAG + cited reports (Phase 14, Decision 012); compression + injection defense (Phase 15, Decision 013). **Phase 13.5 MCP was descoped to an optional post-v1 add-on** ([issue #35](https://github.com/xy9iao/ai-stock-analyst/issues/35)). Project is now in demand-gated maintenance.

## 1. Purpose

This document defines how AI should be used in the MVP version of AI Stock Analyst.

The goal is to design AI behavior, report structure, chat behavior, context packaging, and recommendation style.

The AI system should help beginner investors understand market events, review holdings, analyze watchlist stocks, and make more informed investment decisions.

## 2. AI Role

The AI should act as an investment research assistant.

It should not act as an automated trading bot.

The AI is responsible for:

- Summarizing market news
- Explaining price movements
- Reviewing holdings
- Reviewing watchlist stocks
- Generating investment reports
- Answering investment-related questions
- Explaining beginner stock concepts
- Suggesting possible actions with reasoning

The AI should provide analysis support, not guaranteed financial advice.

## 3. AI Response Style

The AI should use a conclusion-first style.

The preferred response order is:

1. Direct conclusion
2. Suggested action
3. Short reasoning
4. Long-term investment view
5. Swing trading view
6. Beginner-friendly explanation
7. Optional risks or uncertainty
8. Follow-up questions or next steps

The user should not need to read a long report before understanding the main recommendation.

## 4. Beginner-Friendly Explanation

The MVP is designed for beginner investors.

The AI should avoid unnecessary financial jargon.

When financial terms are needed, the AI should explain them using entry-level terminology.

Example:

Instead of only saying:

```txt
Valuation compression is caused by higher discount rates.
```

The AI should explain:

```txt
When interest rates stay high, investors usually pay less for future growth. This can pressure high-growth tech stocks even if the company is still strong.
```

The AI should be practical and clear rather than overly academic.

## 5. Report Format

The MVP report output should be displayed as Markdown in the app.

The MVP does not require structured JSON output for reports.

Markdown is preferred because:

- It is easy to render in the frontend
- It is easy to export to Obsidian
- It is readable for users
- It is flexible during early development

Future versions may use structured JSON internally and render it into Markdown or UI components.

## 6. Report Types

The MVP should support several AI report types.

### 6.1 Overall Market + Portfolio Report

Generated from the Dashboard.

This report combines:

- Market index data
- Macro news
- Holdings
- Watchlist
- Important company news
- Latest financial snapshots when available

The report should help the user understand the overall market and decide what to do with current holdings or watchlist stocks.

### 6.2 Holdings Analysis Report

Generated from the Holdings page.

This report focuses on stocks the user already owns.

It should help answer:

- Which holdings need attention?
- Which positions are doing well or poorly?
- Should the user hold, add, reduce, sell, or wait?
- Are there any important news events affecting the holdings?
- Is the current portfolio too concentrated or exposed to one theme?

### 6.3 Watchlist Opportunity Report

Generated from the Watchlist page.

This report focuses on stocks the user is watching but may not own.

It should help answer:

- Which watchlist stocks look interesting?
- Which stocks should be avoided for now?
- Which stocks need more research?
- Are there possible entry opportunities?
- What news or price movement matters?

### 6.4 Single Stock Analysis Report

Generated from the Stock Detail page.

This report focuses on one ticker.

It should include:

- Current situation
- Recent price movement
- Relevant news
- Latest financial snapshot if available
- Long-term investment view
- Swing trading view
- Suggested action
- Confidence level
- Beginner-friendly explanation

### 6.5 Chat Response

Generated from the Chat page.

The chatbot should answer investment-related questions using available context when useful.

## 7. Stock Selection in Reports

The AI should not mechanically analyze every stock in every report.

For MVP reports, the AI should focus on important or relevant stocks.

A stock may be considered important if:

- It is in the user's holdings
- It has a large daily price movement
- It has important news
- It affects the user's portfolio heavily
- It is a major watchlist opportunity
- It is related to major market or sector movement
- It has a meaningful earnings or financial update

The report should avoid wasting space on stocks where nothing meaningful happened.

## 8. Action Labels

The AI may assign action labels to important stocks.

Supported action labels:

- Strong Buy
- Buy
- Add Gradually
- Hold
- Wait
- Reduce
- Sell
- Avoid

Action labels should be used carefully.

Each action label should include reasoning.

The UI may display action labels with different colors and visual styles.

The color mapping will be decided during UI design.

## 9. Strategy Suggestions

The AI should not only output an action label.

It should also explain a possible strategy.

Example strategies:

- Long-term DCA
- Hold and monitor
- Add on pullback
- Wait for better entry
- Reduce exposure
- Research further
- Short-term swing only
- Avoid for now

The strategy should match the user's likely goal and risk level.

## 10. Long-Term View and Swing View

AI analysis should separate long-term investment view from short-term swing trading view.

### 10.1 Long-Term Investment View

This section should focus on:

- Company fundamentals
- Long-term business outlook
- Sector trend
- Macro environment
- Valuation concern if available
- Whether the stock fits long-term investing or DCA

### 10.2 Swing Trading View

This section should focus on:

- Recent price movement
- Short-term news
- Momentum
- Market sentiment
- Entry timing
- Whether it is better to wait, add gradually, or avoid chasing

The MVP should prioritize long-term investing, but still include light swing trading analysis when useful.

## 11. Risk Section

A risk section is not mandatory for every report.

The AI should include risks when they are useful or important.

Examples of when to include risks:

- A stock has high volatility
- A stock has negative news
- A stock has weak financial performance
- A position is too concentrated
- Macro conditions are unfavorable
- The AI recommendation has low confidence
- Data is missing or incomplete

The AI should not force a generic risk section if there is no meaningful risk to discuss.

## 12. Confidence Level

The AI should include a confidence level when making an action-oriented recommendation.

Supported confidence levels:

- Low
- Medium
- High

Confidence should depend on:

- Data quality
- Strength of news signal
- Price movement clarity
- Financial data availability
- Consistency between macro, news, and price movement
- Whether the conclusion is speculative

The AI should avoid overconfidence when data is incomplete.

## 13. Chat Context

The Chat page should be able to use relevant context from the system.

Possible context sources:

- User holdings
- User watchlist
- Recent reports
- Recent market data
- Recent company news
- Latest financial snapshots
- Stock notes
- Investment thesis

The MVP should start with simple context injection.

RAG or agent-based workflows can be considered later if needed.

## 14. RAG and Agent Considerations

The MVP does not require a complex RAG system or full agent workflow.

However, the system should be designed so these can be added later.

### 14.1 Simple MVP Context Injection

For MVP, the backend can directly load relevant context from the database and API responses.

Example:

```txt
User asks about NVDA
    ↓
Backend loads NVDA from holdings/watchlist if available
    ↓
Backend loads recent NVDA market data
    ↓
Backend loads recent NVDA news
    ↓
Backend loads latest report if relevant
    ↓
Backend sends compact context to LLM
```

### 14.2 Future RAG

RAG may be useful later for:

- Searching past reports
- Searching chat history
- Searching company thesis notes
- Searching SEC filings
- Searching earnings call transcripts
- Searching long research documents

### 14.3 Future Agent Workflow

Agent workflows may be useful later for:

- Multi-step research
- Automatic data gathering
- Comparing multiple companies
- Generating deeper reports
- Rechecking uncertain information
- Creating investment memo drafts

The MVP should not start with a complex agent system.

## 15. Prompt Building

The backend should build prompts in a structured way.

The frontend should not directly construct prompts.

Prompt building should happen inside the backend AI module.

Possible prompt components:

- System role
- User request
- Report type
- Holdings context
- Watchlist context
- Market data context
- News context
- Financial snapshot context
- Output format instruction
- Financial advice boundary
- Beginner-friendly explanation instruction

## 16. Context Packaging

The backend should not send raw API responses directly to the LLM.

The backend should transform data into compact structured context.

Example context package:

```txt
Report Type: Holdings Analysis

Market Context:
- S&P 500: +0.8%
- Nasdaq: +1.1%
- Macro headline summary: ...

Holdings:
- NVDA
  - Shares: 3
  - Average cost: 850
  - Current price: 920
  - Daily change: +2.3%
  - Unrealized gain/loss: +8.2%
  - Recent news: ...
  - Latest financial snapshot: ...

- MSFT
  - Shares: 2
  - Average cost: 410
  - Current price: 430
  - Daily change: -0.5%
  - Unrealized gain/loss: +4.8%
  - Recent news: ...
```

This improves:

- Token efficiency
- Report consistency
- Cost control
- AI reasoning quality

## 17. News Context Strategy

The MVP should not send full articles to the LLM.

The news context should include:

- Headline
- Related ticker
- Published date
- Short description or summary if available
- Source name if available

Article links are not required in the prompt for MVP.

The goal is to save tokens while still giving the AI enough context.

## 18. Financial Snapshot Strategy

The MVP should send compact financial snapshots instead of full financial statements.

Example:

```txt
Latest Financial Snapshot:
- Revenue
- Revenue growth
- EPS
- Net income
- Margin if available
- Latest earnings date
- Next earnings date if available
```

This gives the AI enough fundamental context without overloading the prompt.

## 19. Chat Scope

The chatbot should only answer questions related to:

- Stocks
- Investing
- Market news
- User holdings
- Watchlist
- Macro events
- Company analysis
- Report follow-up
- Beginner investment education
- Prompt writing for financial models

The chatbot should not behave as a general-purpose assistant.

If the user asks unrelated questions, the chatbot should redirect the user back to investment-related topics.

## 20. AI Safety and Recommendation Boundary

The AI can provide action-oriented suggestions, but it should not claim certainty.

The system should avoid language such as:

- Guaranteed profit
- Risk-free investment
- You must buy
- This will definitely go up
- This is financial advice

Preferred language:

- Based on available data
- A reasonable action may be
- Consider
- This suggests
- The risk is
- Confidence is low/medium/high
- Further research is needed

The user is responsible for final investment decisions.

## 21. Report Output Template

A typical report should follow this structure:

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

## 22. MVP AI Acceptance Criteria

The MVP AI system is successful if:

- It can generate a Markdown report.
- It starts with a clear conclusion.
- It gives action labels only for important stocks.
- It separates long-term investment view and swing trading view.
- It can use holdings and watchlist data as context.
- It can answer investment-related chat questions.
- It can explain concepts in beginner-friendly language.
- It avoids unnecessary token usage.
- It avoids guaranteed financial advice language.
- It can work without a complex RAG or agent system in the first version.