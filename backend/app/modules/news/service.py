"""Cache-aware company-news orchestration (cache-aside over the shared cache)."""

from sqlalchemy.orm import Session

from app.core import cache
from app.modules.news.provider import NewsProvider
from app.modules.news.schemas import CompanyNews

_PROVIDER_NAME = "yfinance"
_NEWS_TTL_SECONDS = 900  # ~15 minutes


def _get_provider() -> NewsProvider:
    """The news provider (yfinance only for now). Lazy import keeps yfinance off the import path."""
    from app.modules.news.providers.yfinance_news_provider import YFinanceNewsProvider

    return YFinanceNewsProvider()


def get_company_news(db: Session, ticker: str) -> CompanyNews:
    symbol = ticker.strip().upper()
    cache_key = f"{_PROVIDER_NAME}:news:{symbol}"

    cached = cache.get_fresh_payload(db, cache_key)
    if cached is not None:
        return CompanyNews.model_validate(cached)

    news = _get_provider().get_company_news(symbol)
    cache.upsert_payload(
        db, cache_key, _PROVIDER_NAME, news.model_dump(mode="json"), _NEWS_TTL_SECONDS
    )
    return news
