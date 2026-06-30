"""The company-news provider interface (structural Protocol, like MarketDataProvider)."""

from typing import Protocol

from app.modules.news.schemas import CompanyNews


class NewsProvider(Protocol):
    def get_company_news(self, ticker: str) -> CompanyNews:
        """Return recent company news, or raise AppError(404) if the ticker is unknown."""
        ...
