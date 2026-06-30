"""Normalized, compact financial-snapshot shape (not full statements)."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class FinancialSnapshot(BaseModel):
    """A latest-financials snapshot + basic profile for one ticker.

    All numeric fields are optional — providers fill in what they have.
    """

    ticker: str
    company_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: Decimal | None = None
    revenue: Decimal | None = None
    revenue_growth: Decimal | None = None
    eps: Decimal | None = None
    net_income: Decimal | None = None
    gross_margin: Decimal | None = None
    operating_margin: Decimal | None = None
    last_earnings_date: date | None = None
    next_earnings_date: date | None = None
