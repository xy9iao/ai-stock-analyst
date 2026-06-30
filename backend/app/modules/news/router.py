"""HTTP routes for company news."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.news import service
from app.modules.news.schemas import CompanyNews

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/{ticker}")
def get_company_news(ticker: str, db: Session = Depends(get_db)) -> CompanyNews:
    return service.get_company_news(db, ticker)
