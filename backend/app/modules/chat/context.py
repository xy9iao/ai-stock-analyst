"""Assemble the compact chat context block from the toggled options.

Modular: each enabled flag contributes one block; nothing enabled -> "".
Reuses the Phase 6 ai/context helpers for holdings + single-stock data.
"""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.ai import context as ai_context
from app.modules.ai import repository as reports_repo
from app.modules.chat.schemas import ChatContextOptions
from app.modules.watchlist import repository as watchlist_repo

_MAX_REPORTS = 5


def build_context(db: Session, options: ChatContextOptions) -> str:
    blocks: list[str] = []

    if options.include_holdings:
        blocks.append("Portfolio:\n" + ai_context.build_portfolio_context(db))

    if options.ticker:
        symbol = options.ticker.strip().upper()
        try:
            blocks.append("Focus stock:\n" + ai_context.build_single_stock_context(db, symbol))
        except AppError:
            blocks.append(f"Focus stock {symbol}: market data unavailable.")

    if options.include_watchlist:
        items = watchlist_repo.list_items(db)
        if items:
            lines = [
                f"- {w.ticker}" + (f" ({w.reason_to_watch})" if w.reason_to_watch else "")
                for w in items
            ]
            blocks.append("Watchlist:\n" + "\n".join(lines))

    if options.include_recent_reports:
        reports = reports_repo.list_reports(db, limit=_MAX_REPORTS)
        if reports:
            lines = [f"- {r.title} ({r.report_type})" for r in reports]
            blocks.append("Recent reports:\n" + "\n".join(lines))

    return "\n\n".join(blocks)
