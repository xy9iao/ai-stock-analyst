"""Cache-aware financials orchestration (cache-aside over the shared cache)."""

from sqlalchemy.orm import Session

from app.core import cache
from app.modules.financials.provider import FinancialDataProvider
from app.modules.financials.schemas import FinancialSnapshot

_PROVIDER_NAME = "yfinance"
_SNAPSHOT_TTL_SECONDS = 86400  # ~1 day


def _get_provider() -> FinancialDataProvider:
    """The financials provider (yfinance only for now); lazy import keeps yfinance off the path."""
    from app.modules.financials.providers.yfinance_financials_provider import (
        YFinanceFinancialsProvider,
    )

    return YFinanceFinancialsProvider()


def get_snapshot(db: Session, ticker: str) -> FinancialSnapshot:
    symbol = ticker.strip().upper()
    cache_key = f"{_PROVIDER_NAME}:financials:{symbol}"

    cached = cache.get_fresh_payload(db, cache_key)
    if cached is not None:
        return FinancialSnapshot.model_validate(cached)

    snapshot = _get_provider().get_snapshot(symbol)
    cache.upsert_payload(
        db, cache_key, _PROVIDER_NAME, snapshot.model_dump(mode="json"), _SNAPSHOT_TTL_SECONDS
    )
    return snapshot
