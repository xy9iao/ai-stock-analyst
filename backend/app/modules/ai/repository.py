"""Database access for AI reports (the reports table)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Report


def create_report(db: Session, report_type: str, title: str, content_markdown: str) -> Report:
    report = Report(report_type=report_type, title=title, content_markdown=content_markdown)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, limit: int = 50) -> list[Report]:
    rows = db.scalars(select(Report).order_by(Report.created_at.desc()).limit(limit)).all()
    return list(rows)


def get_report(db: Session, report_id: int) -> Report | None:
    return db.get(Report, report_id)
