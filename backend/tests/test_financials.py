"""Tests for the financials API. The provider is mocked — no live network calls."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.modules.financials import service
from app.modules.financials.schemas import FinancialSnapshot


class FakeFinancialsProvider:
    """Returns a snapshot, or raises 404 for ticker 'MISSING'; counts calls."""

    def __init__(self) -> None:
        self.calls = 0

    def get_snapshot(self, ticker: str) -> FinancialSnapshot:
        self.calls += 1
        if ticker == "MISSING":
            raise AppError("ticker_not_found", f"No financial data for {ticker}", 404)
        return FinancialSnapshot(
            ticker=ticker,
            company_name="NVIDIA Corporation",
            sector="Technology",
            market_cap=Decimal("4722368446464"),
            revenue=Decimal("253491003392"),
            eps=Decimal("6.53"),
        )


@pytest.fixture
def fake_financials(monkeypatch: pytest.MonkeyPatch) -> FakeFinancialsProvider:
    provider = FakeFinancialsProvider()
    monkeypatch.setattr(service, "_get_provider", lambda: provider)
    return provider


def test_financials_normalizes_and_caches(
    client: TestClient, fake_financials: FakeFinancialsProvider
) -> None:
    first = client.get("/api/financials/nvda")
    assert first.status_code == 200
    body = first.json()
    assert body["ticker"] == "NVDA"
    assert body["company_name"] == "NVIDIA Corporation"
    assert Decimal(body["market_cap"]) == Decimal("4722368446464")  # large int stays exact

    second = client.get("/api/financials/NVDA")  # same key -> cache hit
    assert second.status_code == 200
    assert fake_financials.calls == 1


def test_financials_unknown_returns_404(
    client: TestClient, fake_financials: FakeFinancialsProvider
) -> None:
    res = client.get("/api/financials/MISSING")
    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "ticker_not_found"
