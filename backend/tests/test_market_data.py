"""Tests for the market_data API. The provider is mocked — no live network calls."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.modules.market_data import service
from app.modules.market_data.schemas import Candle, HistoryRange, PriceHistory, Quote


class FakeProvider:
    """In-memory provider stub: counts calls and raises 404 for the ticker 'MISSING'."""

    def __init__(self) -> None:
        self.quote_calls = 0
        self.history_calls = 0

    def get_quote(self, ticker: str) -> Quote:
        self.quote_calls += 1
        if ticker == "MISSING":
            raise AppError("ticker_not_found", f"No data for {ticker}", 404)
        return Quote(
            ticker=ticker,
            price=Decimal("100.0000"),
            change=Decimal("1.0000"),
            change_percent=Decimal("1.0101"),
            previous_close=Decimal("99.0000"),
        )

    def get_price_history(self, ticker: str, range: HistoryRange) -> PriceHistory:
        self.history_calls += 1
        if ticker == "MISSING":
            raise AppError("ticker_not_found", f"No history for {ticker}", 404)
        candle = Candle(
            timestamp=datetime(2026, 1, 2, tzinfo=UTC),
            open=Decimal("99.0000"),
            high=Decimal("101.0000"),
            low=Decimal("98.0000"),
            close=Decimal("100.0000"),
            volume=1000,
        )
        return PriceHistory(ticker=ticker, range=range, candles=[candle])


@pytest.fixture
def fake_provider(monkeypatch: pytest.MonkeyPatch) -> FakeProvider:
    provider = FakeProvider()
    monkeypatch.setattr(service, "_get_provider", lambda: provider)
    return provider


def test_quote_normalizes_and_caches(client: TestClient, fake_provider: FakeProvider) -> None:
    first = client.get("/api/market/quote/nvda")
    assert first.status_code == 200
    body = first.json()
    assert body["ticker"] == "NVDA"  # service normalized the symbol
    assert Decimal(body["price"]) == Decimal("100.0000")

    second = client.get("/api/market/quote/NVDA")  # same key -> served from cache
    assert second.status_code == 200
    assert fake_provider.quote_calls == 1  # provider hit only once


def test_quote_unknown_ticker_404(client: TestClient, fake_provider: FakeProvider) -> None:
    res = client.get("/api/market/quote/MISSING")
    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "ticker_not_found"


def test_history_valid_range_200(client: TestClient, fake_provider: FakeProvider) -> None:
    res = client.get("/api/market/history/nvda?range=1m")
    assert res.status_code == 200
    body = res.json()
    assert body["ticker"] == "NVDA"
    assert body["range"] == "1m"
    assert len(body["candles"]) == 1


def test_history_bad_range_422(client: TestClient, fake_provider: FakeProvider) -> None:
    res = client.get("/api/market/history/nvda?range=10y")
    assert res.status_code == 422
    assert fake_provider.history_calls == 0  # rejected before reaching the provider


def test_history_unknown_ticker_404(client: TestClient, fake_provider: FakeProvider) -> None:
    res = client.get("/api/market/history/MISSING?range=1d")
    assert res.status_code == 404


def test_history_caches_per_range(client: TestClient, fake_provider: FakeProvider) -> None:
    client.get("/api/market/history/nvda?range=1w")
    client.get("/api/market/history/NVDA?range=1w")  # same range -> cache hit
    assert fake_provider.history_calls == 1
