"""Normalized, provider-agnostic market-data shapes.

These are the only market-data types the rest of the app sees. Raw provider
payloads (yfinance DataFrames, vendor JSON) are converted into these in the
provider layer and never leak past it.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class HistoryRange(str, Enum):
    """Supported chart ranges. Typing a param as this gives free 422 validation."""

    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    ONE_YEAR = "1y"


class Quote(BaseModel):
    """A current snapshot quote for one ticker."""

    ticker: str
    price: Decimal
    change: Decimal  # price - previous_close
    change_percent: Decimal  # change / previous_close * 100
    previous_close: Decimal
    open: Decimal | None = None
    day_high: Decimal | None = None
    day_low: Decimal | None = None
    volume: int | None = None
    as_of: datetime | None = None


class Candle(BaseModel):
    """One OHLCV bar in a price-history series."""

    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class PriceHistory(BaseModel):
    """A series of OHLCV bars for one ticker over a range."""

    ticker: str
    range: HistoryRange
    candles: list[Candle]
