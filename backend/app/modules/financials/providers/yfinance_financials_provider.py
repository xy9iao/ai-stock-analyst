"""yfinance-backed FinancialDataProvider (no API key).

Maps yfinance's `.info` + `.calendar` into a compact FinancialSnapshot.
The only place yfinance financials are imported.
"""

import math
from datetime import UTC, date, datetime
from decimal import Decimal

import yfinance as yf

from app.core.errors import AppError
from app.modules.financials.schemas import FinancialSnapshot


def _to_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, int):
        return Decimal(value)  # keep large ints (revenue, market cap) clean
    number = float(value)
    if math.isnan(number):
        return None
    return Decimal(str(number))


def _epoch_to_date(value: object) -> date | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=UTC).date()
    except (TypeError, ValueError, OSError):
        return None


def _next_earnings_date(calendar: object) -> date | None:
    if not isinstance(calendar, dict):
        return None
    value = calendar.get("Earnings Date")
    if isinstance(value, list):
        value = value[0] if value else None
    return value if isinstance(value, date) else None


class YFinanceFinancialsProvider:
    """Concrete FinancialDataProvider backed by yfinance's `.info` + `.calendar`."""

    def get_snapshot(self, ticker: str) -> FinancialSnapshot:
        symbol = ticker.strip().upper()
        yf_ticker = yf.Ticker(symbol)
        try:
            info = yf_ticker.info or {}
        except Exception as exc:  # yfinance raises varied errors on bad symbols / network
            raise AppError(
                code="financials_unavailable",
                message=f"Could not fetch financials for {symbol}",
                status_code=502,
            ) from exc

        company_name = info.get("longName") or info.get("shortName")
        market_cap = _to_decimal(info.get("marketCap"))
        revenue = _to_decimal(info.get("totalRevenue"))
        if company_name is None and market_cap is None and revenue is None:
            raise AppError(
                code="ticker_not_found",
                message=f"No financial data for ticker {symbol}",
                status_code=404,
            )

        try:
            calendar = yf_ticker.calendar
        except Exception:
            calendar = None

        return FinancialSnapshot(
            ticker=symbol,
            company_name=company_name,
            sector=info.get("sector"),
            industry=info.get("industry"),
            market_cap=market_cap,
            revenue=revenue,
            revenue_growth=_to_decimal(info.get("revenueGrowth")),
            eps=_to_decimal(info.get("trailingEps")),
            net_income=_to_decimal(info.get("netIncomeToCommon")),
            gross_margin=_to_decimal(info.get("grossMargins")),
            operating_margin=_to_decimal(info.get("operatingMargins")),
            last_earnings_date=_epoch_to_date(info.get("mostRecentQuarter")),
            next_earnings_date=_next_earnings_date(calendar),
        )
