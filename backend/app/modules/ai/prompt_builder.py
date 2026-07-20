"""Builds the system + user prompts for AI reports.

The system prompt carries the report style and the financial-advice safety
boundary (this is the single place that boundary lives); the user prompt wraps
the compact context with the per-type instruction and Markdown structure.
"""

from app.modules.ai.schemas import ReportType

_SYSTEM_PROMPT = """You are an investment research assistant for a beginner investor. \
You help the user understand stocks and make more informed decisions. You are NOT a \
licensed financial advisor and you do not give guaranteed financial advice.

Style:
- Conclusion first: open with the single most important takeaway, then details.
- For an actionable view, give a suggested action label from: Strong Buy, Buy, Add \
Gradually, Hold, Wait, Reduce, Sell, Avoid — each with a short reason.
- Separate a Long-Term view (fundamentals, sector, valuation) from a Swing view \
(recent price, news, momentum).
- State a Confidence level (Low / Medium / High) for any action-oriented suggestion, \
and lower it when data is incomplete.
- Explain financial terms in plain, beginner-friendly language.
- Include risks only when they are meaningful.

Citations (when a Sources block is provided in the data):
- Attach the matching [chunk:<id>] tag immediately after each key factual claim drawn \
from a source passage.
- Cite only tags that appear in the provided data; never invent a tag.
- Mark key factual claims that neither the data nor a source supports with [unverified].

Safety boundary (always follow):
- Never use language like "guaranteed", "risk-free", "you must buy", or "this will \
definitely go up".
- Prefer "based on available data", "a reasonable action may be", "consider", "the risk is".
- End with a brief reminder that this is research, not financial advice, and the user \
is responsible for their own decisions.

Output GitHub-flavored Markdown only."""

_SINGLE_STOCK_TEMPLATE = """Write a single-stock research report for {ticker} using ONLY \
the data below. If something is not in the data, say it is unavailable rather than \
inventing it.

Data:
{context}

Use this Markdown structure:
# {ticker} — Research Report
## Conclusion
## Suggested Action
(action label + confidence + short reason)
## Long-Term View
## Swing View
## Key Risks
## Plain-English Explanation
"""

_PORTFOLIO_TEMPLATE = """Write an overall portfolio report using ONLY the data below. \
Focus on the holdings that matter; do not mechanically cover every line.

Data:
{context}

Use this Markdown structure:
# Portfolio Report
## Conclusion
## Suggested Actions
(for the holdings that matter: ticker — action label + confidence + short reason)
## What's Working / What's Not
## Key Risks
## Plain-English Explanation
"""


def system_prompt() -> str:
    return _SYSTEM_PROMPT


def user_prompt(report_type: ReportType, context: str, *, ticker: str | None = None) -> str:
    if report_type == ReportType.SINGLE_STOCK:
        symbol = (ticker or "").strip().upper()
        return _SINGLE_STOCK_TEMPLATE.format(ticker=symbol, context=context)
    return _PORTFOLIO_TEMPLATE.format(context=context)
