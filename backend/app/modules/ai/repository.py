"""Database access for AI reports (the reports table)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Report


def create_report(
    db: Session, report_type: str, title: str, content_markdown: str, session_id: str
) -> Report:
    report = Report(
        report_type=report_type,
        title=title,
        content_markdown=content_markdown,
        session_id=session_id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, session_id: str, limit: int = 50) -> list[Report]:
    rows = db.scalars(
        select(Report)
        .where(Report.session_id == session_id)
        .order_by(Report.created_at.desc())
        .limit(limit)
    ).all()
    return list(rows)


def count_reports(db: Session, session_id: str) -> int:
    return len(db.scalars(select(Report.id).where(Report.session_id == session_id)).all())


def get_report(db: Session, report_id: int, session_id: str) -> Report | None:
    report = db.get(Report, report_id)
    if report is not None and report.session_id != session_id:
        return None
    return report
