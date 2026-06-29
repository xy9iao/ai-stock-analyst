"""The market-data provider interface.

`MarketDataProvider` is a structural `Protocol`: any object that has these two
methods satisfies it — a concrete provider does NOT need to inherit from it.
The service depends on this interface, never on a specific vendor, so providers
are swappable by config alone.
"""

from typing import Protocol

from app.modules.market_data.schemas import HistoryRange, PriceHistory, Quote


class MarketDataProvider(Protocol):
    def get_quote(self, ticker: str) -> Quote:
        """Return a current quote, or raise AppError(404) if the ticker is unknown."""
        ...

    def get_price_history(self, ticker: str, range: HistoryRange) -> PriceHistory:
        """Return OHLCV history for the ticker over the given range."""
        ...
