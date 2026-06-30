"""Orchestrates report generation: context -> prompt -> LLM -> store -> return."""

from sqlalchemy.orm import Session

from app.models import Report
from app.modules.ai import context, llm_client, prompt_builder, repository
from app.modules.ai.schemas import ReportRequest, ReportType


def generate_report(db: Session, request: ReportRequest) -> Report:
    if request.report_type == ReportType.SINGLE_STOCK:
        ticker = (request.ticker or "").strip().upper()
        # build_single_stock_context raises AppError(404) for an unknown ticker.
        report_context = context.build_single_stock_context(db, ticker)
        user = prompt_builder.user_prompt(ReportType.SINGLE_STOCK, report_context, ticker=ticker)
        title = f"{ticker} — Research Report"
    else:
        report_context = context.build_portfolio_context(db)
        user = prompt_builder.user_prompt(ReportType.PORTFOLIO, report_context)
        title = "Portfolio Report"

    markdown = llm_client.complete(prompt_builder.system_prompt(), user)
    return repository.create_report(
        db,
        report_type=request.report_type.value,
        title=title,
        content_markdown=markdown,
    )
