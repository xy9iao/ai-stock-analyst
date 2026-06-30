"""HTTP routes for financial snapshots."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.financials import service
from app.modules.financials.schemas import FinancialSnapshot

router = APIRouter(prefix="/api/financials", tags=["financials"])


@router.get("/{ticker}")
def get_snapshot(ticker: str, db: Session = Depends(get_db)) -> FinancialSnapshot:
    return service.get_snapshot(db, ticker)
