"""HTTP routes for market data (quotes + price history)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.market_data import service
from app.modules.market_data.schemas import HistoryRange, PriceHistory, Quote

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/quote/{ticker}")
def get_quote(ticker: str, db: Session = Depends(get_db)) -> Quote:
    return service.get_quote(db, ticker)


@router.get("/history/{ticker}")
def get_price_history(
    ticker: str,
    range: HistoryRange = HistoryRange.ONE_DAY,
    db: Session = Depends(get_db),
) -> PriceHistory:
    return service.get_price_history(db, ticker, range)
