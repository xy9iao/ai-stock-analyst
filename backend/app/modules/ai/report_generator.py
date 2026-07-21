"""Orchestrates report generation: context -> prompt -> LLM -> store -> return."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.models import Report
from app.modules.ai import context, llm_client, prompt_builder, repository
from app.modules.ai.agent import loop
from app.modules.ai.rag import citations, retrieval
from app.modules.ai.schemas import ReportRequest, ReportType

_TITLE_MAX = 80

_CITATION_RETRY_SUFFIX = (
    "\n\nIMPORTANT: your previous draft cited [chunk:<id>] tags that do not exist in "
    "the provided Sources block. Regenerate the report citing ONLY tags that appear "
    "in the data; mark unsupported key claims with [unverified]."
)


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

    source_chunks: list = []
    if request.report_type == ReportType.SINGLE_STOCK:
        ticker = (request.ticker or "").strip().upper()
        # build_single_stock_context raises AppError(404) for an unknown ticker.
        report_context = context.build_single_stock_context(db, ticker, session_id)
        # Fixed retrieval step (Decision 011: closed data needs -> deterministic
        # retrieval). Failure here degrades to an uncited report, never an error.
        try:
            source_chunks = retrieval.hybrid_search(
                db, f"{ticker} recent developments and outlook", ticker=ticker
            )
        except Exception:
            source_chunks = []
        if source_chunks:
            report_context += "\n\n" + citations.format_sources(source_chunks)
        user = prompt_builder.user_prompt(ReportType.SINGLE_STOCK, report_context, ticker=ticker)
        title = f"{ticker} — Research Report"
    else:
        report_context = context.build_portfolio_context(db, session_id)
        user = prompt_builder.user_prompt(ReportType.PORTFOLIO, report_context)
        title = "Portfolio Report"

    markdown = llm_client.complete(
        prompt_builder.system_prompt(), user, db=db, session_id=session_id, kind="report"
    )
    if source_chunks:
        allowed = {chunk.id for chunk in source_chunks}
        if citations.invalid_ids(db, markdown, allowed):
            # One corrective retry on hallucinated tags; render() strips survivors.
            markdown = llm_client.complete(
                prompt_builder.system_prompt(),
                user + _CITATION_RETRY_SUFFIX,
                db=db,
                session_id=session_id,
                kind="report",
            )
        markdown = citations.render(db, markdown, allowed)
    return repository.create_report(
        db,
        report_type=request.report_type.value,
        title=title,
        content_markdown=markdown,
        session_id=session_id,
    )


def generate_research_memo(db: Session, request: ReportRequest, session_id: str) -> Report:
    """Run the agent loop for an open-ended query and archive the memo as a report.

    Research memos count against the same per-session report cap as pipeline
    reports (cost-defense layer 3 covers the agent path with no new infra).
    """
    _enforce_demo_cap(db, session_id)

    query = (request.query or "").strip()
    result = loop.run_research(db, session_id, query)
    # Agent path: the loop does not track retrieved ids, so validation is
    # DB-existence (weaker, known limit); no retry — the run is already over.
    memo = citations.render(db, result.memo)

    title = query if len(query) <= _TITLE_MAX else query[: _TITLE_MAX - 1] + "…"
    return repository.create_report(
        db,
        report_type=ReportType.RESEARCH.value,
        title=title,
        content_markdown=memo,
        session_id=session_id,
    )
