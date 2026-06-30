"""Normalized, provider-agnostic company-news shapes (compact metadata only)."""

from datetime import datetime

from pydantic import BaseModel


class NewsItem(BaseModel):
    """One compact news headline — never the full article body."""

    headline: str
    source: str | None = None
    published_at: datetime | None = None
    summary: str | None = None
    url: str | None = None


class CompanyNews(BaseModel):
    """Recent news for one ticker (wrapper so the cache payload stays a dict)."""

    ticker: str
    items: list[NewsItem]
