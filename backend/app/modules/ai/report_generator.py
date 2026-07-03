"""Orchestrates report generation: context -> prompt -> LLM -> store -> return."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.models import Report
from app.modules.ai import context, llm_client, prompt_builder, repository
from app.modules.ai.schemas import ReportRequest, ReportType


def _enforce_demo_cap(db: Session, session_id: str) -> None:
    """Cost-defense layer 3: per-session report cap (demo mode only)."""
    if not settings.demo_mode:
        return
    if repository.count_reports(db, session_id) >= settings.demo_report_limit:
        raise AppError(
            code="demo_report_limit",
            message=(
                f"Demo limit reached: max {settings.demo_report_limit} reports per session. "
                "Start a new demo session to continue."
            ),
            status_code=429,
        )


def generate_report(db: Session, request: ReportRequest, session_id: str) -> Report:
    _enforce_demo_cap(db, session_id)

    if request.report_type == ReportType.SINGLE_STOCK:
        ticker = (request.ticker or "").strip().upper()
        # build_single_stock_context raises AppError(404) for an unknown ticker.
        report_context = context.build_single_stock_context(db, ticker, session_id)
        user = prompt_builder.user_prompt(ReportType.SINGLE_STOCK, report_context, ticker=ticker)
        title = f"{ticker} — Research Report"
    else:
        report_context = context.build_portfolio_context(db, session_id)
        user = prompt_builder.user_prompt(ReportType.PORTFOLIO, report_context)
        title = "Portfolio Report"

    markdown = llm_client.complete(
        prompt_builder.system_prompt(), user, db=db, session_id=session_id, kind="report"
    )
    return repository.create_report(
        db,
        report_type=request.report_type.value,
        title=title,
        content_markdown=markdown,
        session_id=session_id,
    )
