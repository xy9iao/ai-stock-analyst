"""Cache-aware market-data orchestration (the cache-aside pattern)."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.modules.market_data import repository
from app.modules.market_data.provider import MarketDataProvider
from app.modules.market_data.schemas import HistoryRange, PriceHistory, Quote

_QUOTE_TTL_SECONDS = 120
_HISTORY_TTL_SECONDS: dict[HistoryRange, int] = {
    HistoryRange.ONE_DAY: 300,
    HistoryRange.ONE_WEEK: 900,
    HistoryRange.ONE_MONTH: 3600,
    HistoryRange.ONE_YEAR: 86400,
}


def _get_provider() -> MarketDataProvider:
    """Select the configured provider. Lazy import keeps heavy vendor deps off the import path."""
    name = settings.market_data_provider.lower()
    if name == "yfinance":
        from app.modules.market_data.providers.yfinance_provider import YFinanceProvider

        return YFinanceProvider()
    raise AppError(
        code="unknown_market_data_provider",
        message=f"Unknown market data provider: {name}",
        status_code=500,
    )


def get_quote(db: Session, ticker: str) -> Quote:
    symbol = ticker.strip().upper()
    provider_name = settings.market_data_provider.lower()
    cache_key = f"{provider_name}:quote:{symbol}"

    cached = repository.get_fresh_payload(db, cache_key)
    if cached is not None:
        return Quote.model_validate(cached)

    quote = _get_provider().get_quote(symbol)
    repository.upsert_payload(
        db, cache_key, provider_name, quote.model_dump(mode="json"), _QUOTE_TTL_SECONDS
    )
    return quote


def get_price_history(db: Session, ticker: str, range: HistoryRange) -> PriceHistory:
    symbol = ticker.strip().upper()
    provider_name = settings.market_data_provider.lower()
    cache_key = f"{provider_name}:history:{symbol}:{range.value}"

    cached = repository.get_fresh_payload(db, cache_key)
    if cached is not None:
        return PriceHistory.model_validate(cached)

    history = _get_provider().get_price_history(symbol, range)
    repository.upsert_payload(
        db,
        cache_key,
        provider_name,
        history.model_dump(mode="json"),
        _HISTORY_TTL_SECONDS[range],
    )
    return history
