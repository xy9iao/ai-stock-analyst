"""yfinance-backed MarketDataProvider (local default; no API key).

The only place yfinance is imported. Converts yfinance's pandas/float output
into the normalized market_data schemas; unknown tickers become AppError(404).
"""

import math
from datetime import UTC, datetime
from decimal import Decimal

import yfinance as yf

from app.core.errors import AppError
from app.modules.market_data.schemas import Candle, HistoryRange, PriceHistory, Quote

# HistoryRange -> (yfinance period, yfinance interval)
_RANGE_TO_YF: dict[HistoryRange, tuple[str, str]] = {
    HistoryRange.ONE_DAY: ("1d", "5m"),
    HistoryRange.ONE_WEEK: ("5d", "30m"),
    HistoryRange.ONE_MONTH: ("1mo", "1d"),
    HistoryRange.ONE_YEAR: ("1y", "1d"),
}


# Quantize prices to strip binary-float noise (e.g. 192.52999877929688 -> 192.5300).
_PRICE_QUANTUM = Decimal("0.0001")


def _to_decimal(value: object) -> Decimal | None:
    """yfinance float/int -> Decimal (quantized); None/NaN treated as missing."""
    if value is None:
        return None
    number = float(value)
    if math.isnan(number):
        return None
    return Decimal(str(number)).quantize(_PRICE_QUANTUM)


def _to_int(value: object) -> int | None:
    if value is None:
        return None
    number = float(value)
    if math.isnan(number):
        return None
    return int(number)


def _attr(obj: object, name: str) -> object:
    """Best-effort optional attribute read from yfinance's FastInfo."""
    try:
        return getattr(obj, name)
    except Exception:
        return None


class YFinanceProvider:
    """Concrete MarketDataProvider backed by yfinance (structurally satisfies the Protocol)."""

    def get_quote(self, ticker: str) -> Quote:
        symbol = ticker.strip().upper()
        fast = yf.Ticker(symbol).fast_info
        try:
            price = _to_decimal(fast.last_price)
            previous_close = _to_decimal(fast.previous_close)
        except Exception as exc:  # yfinance raises varied errors for bad symbols / network
            raise AppError(
                code="market_data_unavailable",
                message=f"Could not fetch quote for {symbol}",
                status_code=502,
            ) from exc

        if price is None or previous_close is None:
            raise AppError(
                code="ticker_not_found",
                message=f"No market data for ticker {symbol}",
                status_code=404,
            )

        change = price - previous_close
        change_percent = (
            (change / previous_close * 100).quantize(_PRICE_QUANTUM)
            if previous_close != 0
            else Decimal("0")
        )
        return Quote(
            ticker=symbol,
            price=price,
            change=change,
            change_percent=change_percent,
            previous_close=previous_close,
            open=_to_decimal(_attr(fast, "open")),
            day_high=_to_decimal(_attr(fast, "day_high")),
            day_low=_to_decimal(_attr(fast, "day_low")),
            volume=_to_int(_attr(fast, "last_volume")),
            as_of=datetime.now(tz=UTC),
        )

    def get_price_history(self, ticker: str, range: HistoryRange) -> PriceHistory:
        symbol = ticker.strip().upper()
        period, interval = _RANGE_TO_YF[range]
        try:
            frame = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=True)
        except Exception as exc:
            raise AppError(
                code="market_data_unavailable",
                message=f"Could not fetch price history for {symbol}",
                status_code=502,
            ) from exc

        if frame.empty:
            raise AppError(
                code="ticker_not_found",
                message=f"No price history for ticker {symbol}",
                status_code=404,
            )

        candles: list[Candle] = []
        for timestamp, row in frame.iterrows():
            close = _to_decimal(row["Close"])
            if close is None:
                continue  # skip incomplete bars
            candles.append(
                Candle(
                    timestamp=timestamp.to_pydatetime(),
                    open=_to_decimal(row["Open"]) or close,
                    high=_to_decimal(row["High"]) or close,
                    low=_to_decimal(row["Low"]) or close,
                    close=close,
                    volume=_to_int(row["Volume"]) or 0,
                )
            )
        return PriceHistory(ticker=symbol, range=range, candles=candles)
