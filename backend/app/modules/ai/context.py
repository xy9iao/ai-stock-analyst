"""Assemble compact, LLM-ready context from DB rows + cached market/news/financials.

Compact text only — never raw API payloads, full articles, or full statements
(planning/ai-design.md §16-18). This is the MVP "DB-context injection" pattern.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.financials import service as financials_service
from app.modules.holdings import repository as holdings_repo
from app.modules.market_data import service as market_service
from app.modules.news import service as news_service
from app.modules.watchlist import repository as watchlist_repo

_MAX_NEWS = 4
_MAX_PORTFOLIO_HOLDINGS = 25


def _financials_line(db: Session, symbol: str) -> str | None:
    """Compact one-line financial snapshot, or None if unavailable."""
    try:
        f = financials_service.get_snapshot(db, symbol)
    except AppError:
        return None
    parts: list[str] = []
    if f.market_cap is not None:
        parts.append(f"market cap {f.market_cap}")
    if f.revenue is not None:
        parts.append(f"revenue {f.revenue}")
    if f.revenue_growth is not None:
        parts.append(f"rev growth {f.revenue_growth}")
    if f.eps is not None:
        parts.append(f"EPS {f.eps}")
    if f.gross_margin is not None:
        parts.append(f"gross margin {f.gross_margin}")
    if f.next_earnings_date is not None:
        parts.append(f"next earnings {f.next_earnings_date}")
    return "Financials: " + ", ".join(parts) if parts else None


def _news_lines(db: Session, symbol: str) -> list[str]:
    try:
        news = news_service.get_company_news(db, symbol)
    except AppError:
        return []
    return [f"- {item.headline} ({item.source})" for item in news.items[:_MAX_NEWS]]


def build_single_stock_context(db: Session, ticker: str, session_id: str) -> str:
    symbol = ticker.strip().upper()
    lines = [f"Ticker: {symbol}"]

    holdings = holdings_repo.list_holdings(db, session_id)
    holding = next((h for h in holdings if h.ticker == symbol), None)
    if holding is not None:
        lines.append(f"User owns {holding.shares} shares at average cost {holding.average_cost}.")
        if holding.investment_thesis:
            lines.append(f"User's thesis: {holding.investment_thesis}")
    watch = next((w for w in watchlist_repo.list_items(db, session_id) if w.ticker == symbol), None)
    if watch is not None and watch.reason_to_watch:
        lines.append(f"On watchlist — reason: {watch.reason_to_watch}")

    # Quote is required: an unknown ticker raises AppError(404), which propagates.
    quote = market_service.get_quote(db, symbol)
    lines.append(
        f"Current price {quote.price}, {quote.change_percent}% today "
        f"(previous close {quote.previous_close})."
    )

    fin = _financials_line(db, symbol)
    if fin:
        lines.append(fin)

    news_lines = _news_lines(db, symbol)
    if news_lines:
        lines.append("Recent news:")
        lines.extend(news_lines)

    return "\n".join(lines)


def build_portfolio_context(db: Session, session_id: str) -> str:
    holdings = holdings_repo.list_holdings(db, session_id)
    if not holdings:
        return "The portfolio has no holdings yet."

    lines = ["Holdings:"]
    for h in holdings[:_MAX_PORTFOLIO_HOLDINGS]:
        try:
            quote = market_service.get_quote(db, h.ticker)
        except AppError:
            lines.append(f"- {h.ticker}: {h.shares} sh @ {h.average_cost} (price unavailable)")
            continue
        unrealized = ""
        if h.average_cost != 0:
            pct = (quote.price - h.average_cost) / h.average_cost * 100
            unrealized = f", unrealized {pct.quantize(Decimal('0.01'))}%"
        lines.append(
            f"- {h.ticker}: {h.shares} sh @ {h.average_cost}; "
            f"price {quote.price} ({quote.change_percent}% today){unrealized}"
        )
    return "\n".join(lines)
