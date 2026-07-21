"""Tests for the AI reports API. The LLM call and context assembly are mocked
(no network, no cost) — the real prompt builder + DB persistence are exercised.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.modules.ai import context, llm_client, report_generator
from app.modules.ai.agent import loop
from app.modules.ai.agent.loop import ResearchResult


@pytest.fixture
def fake_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_client, "complete", lambda system, user, **kw: "# Report\n\nMock body.")
    monkeypatch.setattr(
        context, "build_single_stock_context", lambda db, ticker, session_id: f"ctx:{ticker}"
    )
    monkeypatch.setattr(context, "build_portfolio_context", lambda db, session_id: "portfolio ctx")
    # No corpus in these tests: the fixed retrieval step degrades to an uncited report.
    monkeypatch.setattr(report_generator.retrieval, "hybrid_search", lambda db, q, ticker=None: [])


@pytest.fixture
def fake_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        loop,
        "run_research",
        lambda db, session_id, query: ResearchResult(
            memo=f"# Memo\n\nEvidence for: {query}", steps=3, step_limit_hit=False
        ),
    )


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


def test_generate_research_memo(client: TestClient, fake_agent: None) -> None:
    query = "why did NVDA drop this week?"
    res = client.post("/api/reports", json={"report_type": "research", "query": query})
    assert res.status_code == 201
    body = res.json()
    assert body["report_type"] == "research"
    assert body["title"] == query
    assert "Evidence for: why did NVDA drop this week?" in body["content_markdown"]


def test_research_requires_query(client: TestClient, fake_agent: None) -> None:
    res = client.post("/api/reports", json={"report_type": "research"})
    assert res.status_code == 422

    res = client.post("/api/reports", json={"report_type": "research", "query": "   "})
    assert res.status_code == 422


def test_research_title_truncated(client: TestClient, fake_agent: None) -> None:
    query = "x" * 120
    res = client.post("/api/reports", json={"report_type": "research", "query": query})
    assert res.status_code == 201
    title = res.json()["title"]
    assert len(title) == 80
    assert title.endswith("…")


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

    def _missing(db, ticker, session_id):
        raise AppError("ticker_not_found", f"No data for {ticker}", 404)

    monkeypatch.setattr(context, "build_single_stock_context", _missing)
    res = client.post("/api/reports", json={"report_type": "single_stock", "ticker": "NOPE"})
    assert res.status_code == 404
