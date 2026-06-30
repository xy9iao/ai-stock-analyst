"""Tests for the news API. The provider is mocked — no live network calls."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.modules.news import service
from app.modules.news.schemas import CompanyNews, NewsItem


class FakeNewsProvider:
    """Returns one item, or empty for ticker 'EMPTY'; counts calls."""

    def __init__(self) -> None:
        self.calls = 0

    def get_company_news(self, ticker: str) -> CompanyNews:
        self.calls += 1
        if ticker == "EMPTY":
            return CompanyNews(ticker=ticker, items=[])
        return CompanyNews(
            ticker=ticker,
            items=[
                NewsItem(
                    headline="NVDA hits a new high",
                    source="Yahoo Finance",
                    published_at=datetime(2026, 6, 29, tzinfo=UTC),
                    summary="Shares rallied.",
                    url="https://example.com/a",
                )
            ],
        )


@pytest.fixture
def fake_news(monkeypatch: pytest.MonkeyPatch) -> FakeNewsProvider:
    provider = FakeNewsProvider()
    monkeypatch.setattr(service, "_get_provider", lambda: provider)
    return provider


def test_news_normalizes_and_caches(client: TestClient, fake_news: FakeNewsProvider) -> None:
    first = client.get("/api/news/nvda")
    assert first.status_code == 200
    body = first.json()
    assert body["ticker"] == "NVDA"  # service normalized the symbol
    assert len(body["items"]) == 1
    assert body["items"][0]["headline"] == "NVDA hits a new high"

    second = client.get("/api/news/NVDA")  # same key -> cache hit
    assert second.status_code == 200
    assert fake_news.calls == 1  # provider hit only once


def test_news_empty_returns_200(client: TestClient, fake_news: FakeNewsProvider) -> None:
    res = client.get("/api/news/EMPTY")
    assert res.status_code == 200  # empty news is a valid response, not a 404
    assert res.json()["items"] == []
