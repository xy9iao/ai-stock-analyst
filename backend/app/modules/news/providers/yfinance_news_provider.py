"""yfinance-backed NewsProvider (no API key).

Maps yfinance's nested `.news` items ({"id", "content": {...}}) into compact
NewsItem shapes. The only place yfinance news is imported.
"""

import yfinance as yf

from app.core.errors import AppError
from app.modules.news.schemas import CompanyNews, NewsItem

_MAX_ITEMS = 10


def _first_url(content: dict) -> str | None:
    for key in ("canonicalUrl", "clickThroughUrl"):
        url = (content.get(key) or {}).get("url")
        if url:
            return url
    return None


class YFinanceNewsProvider:
    """Concrete NewsProvider backed by yfinance's `.news`."""

    def get_company_news(self, ticker: str) -> CompanyNews:
        symbol = ticker.strip().upper()
        try:
            raw = yf.Ticker(symbol).news or []
        except Exception as exc:  # yfinance raises varied errors on bad symbols / network
            raise AppError(
                code="news_unavailable",
                message=f"Could not fetch news for {symbol}",
                status_code=502,
            ) from exc

        items: list[NewsItem] = []
        for entry in raw[:_MAX_ITEMS]:
            content = entry.get("content") or {}
            headline = content.get("title")
            if not headline:
                continue
            provider = content.get("provider") or {}
            items.append(
                NewsItem(
                    headline=headline,
                    source=provider.get("displayName"),
                    published_at=content.get("pubDate"),
                    summary=content.get("summary") or content.get("description") or None,
                    url=_first_url(content),
                )
            )
        return CompanyNews(ticker=symbol, items=items)
