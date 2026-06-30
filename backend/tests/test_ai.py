"""Tests for the AI reports API. The LLM call and context assembly are mocked
(no network, no cost) — the real prompt builder + DB persistence are exercised.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.modules.ai import context, llm_client


@pytest.fixture
def fake_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_client, "complete", lambda system, user, **kw: "# Report\n\nMock body.")
    monkeypatch.setattr(context, "build_single_stock_context", lambda db, ticker: f"ctx:{ticker}")
    monkeypatch.setattr(context, "build_portfolio_context", lambda db: "portfolio ctx")


def test_generate_single_stock_report(client: TestClient, fake_ai: None) -> None:
    res = client.post("/api/reports", json={"report_type": "single_stock", "ticker": "nvda"})
    assert res.status_code == 201
    body = res.json()
    assert body["report_type"] == "single_stock"
    assert body["title"] == "NVDA — Research Report"
    assert "Mock body" in body["content_markdown"]
    assert body["id"] >= 1


def test_generate_portfolio_report(client: TestClient, fake_ai: None) -> None:
    res = client.post("/api/reports", json={"report_type": "portfolio"})
    assert res.status_code == 201
    assert res.json()["report_type"] == "portfolio"
    assert res.json()["title"] == "Portfolio Report"


def test_single_stock_requires_ticker(client: TestClient, fake_ai: None) -> None:
    res = client.post("/api/reports", json={"report_type": "single_stock"})
    assert res.status_code == 422  # rejected by the schema validator, before any LLM call


def test_list_and_get_reports(client: TestClient, fake_ai: None) -> None:
    created = client.post("/api/reports", json={"report_type": "portfolio"}).json()

    listing = client.get("/api/reports")
    assert listing.status_code == 200
    assert any(r["id"] == created["id"] for r in listing.json())

    one = client.get(f"/api/reports/{created['id']}")
    assert one.status_code == 200
    assert one.json()["id"] == created["id"]


def test_get_missing_report_404(client: TestClient, fake_ai: None) -> None:
    res = client.get("/api/reports/99999")
    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "report_not_found"


def test_single_stock_unknown_ticker_propagates_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(llm_client, "complete", lambda system, user, **kw: "unused")

    def _missing(db, ticker):
        raise AppError("ticker_not_found", f"No data for {ticker}", 404)

    monkeypatch.setattr(context, "build_single_stock_context", _missing)
    res = client.post("/api/reports", json={"report_type": "single_stock", "ticker": "NOPE"})
    assert res.status_code == 404
