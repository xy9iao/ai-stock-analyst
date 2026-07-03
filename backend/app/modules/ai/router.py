"""HTTP routes for AI reports."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.demo_session import get_session_id
from app.core.errors import AppError
from app.modules.ai import report_generator, repository
from app.modules.ai.schemas import ReportRead, ReportRequest

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> ReportRead:
    return report_generator.generate_report(db, request, session_id)


@router.get("")
def list_reports(
    db: Session = Depends(get_db), session_id: str = Depends(get_session_id)
) -> list[ReportRead]:
    return repository.list_reports(db, session_id)


@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> ReportRead:
    report = repository.get_report(db, report_id, session_id)
    if report is None:
        raise AppError("report_not_found", f"Report {report_id} not found", status_code=404)
    return report
