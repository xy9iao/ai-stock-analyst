"""Cache layer over the market_data_cache table — the only DB access for market data."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MarketDataCache


def _as_utc(value: datetime) -> datetime:
    """Treat naive datetimes (e.g. from SQLite) as UTC so comparisons are safe."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def get_fresh_payload(db: Session, cache_key: str) -> dict | None:
    """Return the cached payload if a row exists and hasn't expired, else None."""
    row = db.scalar(select(MarketDataCache).where(MarketDataCache.cache_key == cache_key))
    if row is None or _as_utc(row.expires_at) <= datetime.now(tz=UTC):
        return None
    return row.payload


def upsert_payload(
    db: Session,
    cache_key: str,
    provider: str,
    payload: dict,
    ttl_seconds: int,
) -> None:
    """Insert a new cache entry or refresh an existing one with a new TTL."""
    now = datetime.now(tz=UTC)
    row = db.scalar(select(MarketDataCache).where(MarketDataCache.cache_key == cache_key))
    if row is None:
        row = MarketDataCache(cache_key=cache_key)
        db.add(row)
    row.provider = provider
    row.payload = payload
    row.fetched_at = now
    row.expires_at = now + timedelta(seconds=ttl_seconds)
    db.commit()
