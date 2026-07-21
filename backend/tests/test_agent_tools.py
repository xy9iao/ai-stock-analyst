"""Tests for the Research Agent tool layer (services and the LLM are mocked)."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.ai.agent import indicators as ind
from app.modules.ai.agent import tools


def _candle(close: float, day: int) -> SimpleNamespace:
    return SimpleNamespace(
        timestamp=f"2026-06-{day:02d}T00:00:00Z",
        open=Decimal(str(close)),
        high=Decimal(str(close + 1)),
        low=Decimal(str(close - 1)),
        close=Decimal(str(close)),
        volume=1000 + day,
    )


def _history(ticker: str, closes: list[float]) -> SimpleNamespace:
    return SimpleNamespace(
        ticker=ticker,
        candles=[_candle(c, i + 1) for i, c in enumerate(closes)],
    )


# --- indicators (pure math) ---


def test_sma_exact() -> None:
    assert ind.sma([1, 2, 3, 4], 2) == 3.5
    assert ind.sma([1, 2], 3) is None


def test_ema_seeded_with_sma() -> None:
    # window=2: seed=(1+2)/2=1.5, k=2/3; then 3*2/3 + 1.5*1/3 = 2.5
    assert ind.ema([1, 2, 3], 2) == pytest.approx(2.5)
    assert ind.ema([1], 2) is None


def test_rsi_bounds_and_all_gains() -> None:
    rising = list(range(1, 20))
    assert ind.rsi([float(x) for x in rising]) == 100.0
    mixed = [
        44.0,
        44.3,
        44.1,
        44.5,
        44.2,
        44.6,
        44.8,
        44.4,
        44.9,
        45.1,
        45.0,
        45.3,
        45.2,
        45.5,
        45.4,
        45.8,
    ]
    value = ind.rsi(mixed)
    assert value is not None and 0 <= value <= 100
    assert ind.rsi([1.0, 2.0]) is None


# --- tool wrappers ---


def test_get_price_history_compact_output(monkeypatch: pytest.MonkeyPatch) -> None:
    closes = [float(100 + i) for i in range(60)]
    monkeypatch.setattr(
        tools.market_service, "get_price_history", lambda db, t, r: _history("NVDA", closes)
    )
    out = tools.get_price_history(None, "s", "nvda", "1m")
    assert "NVDA 1m: close 100.0 -> 159.0 (+59.00%)" in out
    # compact: summary + at most 15 sampled candle lines
    assert len(out.splitlines()) <= 16


def test_get_price_history_invalid_period(monkeypatch: pytest.MonkeyPatch) -> None:
    out = tools.get_price_history(None, "s", "NVDA", "3y")
    assert "Invalid period" in out and "1d, 1w, 1m, 1y" in out


def test_get_financials_skips_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = SimpleNamespace(
        ticker="AAPL",
        company_name="Apple",
        sector=None,
        market_cap=Decimal("3000000000000"),
        revenue=None,
        revenue_growth=None,
        eps=Decimal("6.1"),
        net_income=None,
        gross_margin=None,
        operating_margin=None,
        last_earnings_date=date(2026, 5, 1),
        next_earnings_date=None,
    )
    monkeypatch.setattr(tools.financials_service, "get_snapshot", lambda db, t: snapshot)
    out = tools.get_financials(None, "s", "AAPL")
    assert "company: Apple" in out and "EPS: 6.1" in out
    assert "sector" not in out and "revenue growth" not in out


def test_search_news_query_filter_and_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    items = [
        SimpleNamespace(
            headline=f"Datacenter demand {i}",
            source="Reuters",
            published_at="2026-07-01T00:00:00Z",
            summary="GPUs everywhere",
            url=None,
        )
        for i in range(8)
    ] + [
        SimpleNamespace(
            headline="Unrelated lawsuit", source=None, published_at=None, summary=None, url=None
        )
    ]
    news = SimpleNamespace(ticker="NVDA", items=items)
    monkeypatch.setattr(tools.news_service, "get_company_news", lambda db, t: news)

    out = tools.search_news(None, "s", "NVDA", query="datacenter", limit=3)
    assert out.count("[") == 3 and "Unrelated lawsuit" not in out

    none = tools.search_news(None, "s", "NVDA", query="zzz")
    assert "No news found" in none


def test_compute_indicators_reports_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    closes = [float(100 + (i % 7)) for i in range(120)]
    monkeypatch.setattr(
        tools.market_service, "get_price_history", lambda db, t, r: _history("MSFT", closes)
    )
    out = tools.compute_indicators(None, "s", "MSFT", ["sma20", "bollinger"])
    assert "sma20:" in out
    assert "bollinger: unsupported" in out


def test_extract_bulk_routes_through_gateway(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict = {}

    def fake_complete(system, user, **kw):
        seen.update(kw, system=system, user=user)
        return "- fact"

    monkeypatch.setattr(tools.llm_client, "complete", fake_complete)
    out = tools.extract_bulk(None, "sess-1", ["headline one", "headline two"], "NVDA drop")
    assert out == "- fact"
    assert seen["kind"] == "extract" and seen["session_id"] == "sess-1"
    assert "headline one" in seen["user"] and "NVDA drop" in seen["user"]
    assert tools.extract_bulk(None, "s", [], "x") == "No texts provided."


def test_search_documents_formats_passages(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    chunk = SimpleNamespace(
        id=7,
        title="NVDA article",
        published_at=None,
        source_url="https://x/a",
        content="Data-center revenue grew 40%. " * 40,
    )
    monkeypatch.setattr(
        tools.retrieval, "hybrid_search", lambda db, q, ticker=None, top_k=8: [chunk]
    )
    out = tools.search_documents(None, "s", "revenue growth")
    assert "[chunk:7]" in out and "https://x/a" in out
    assert len(out) < 900  # passage truncated for loop-resend economy


def test_search_documents_empty_corpus_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools.retrieval, "hybrid_search", lambda db, q, ticker=None, top_k=8: [])
    out = tools.search_documents(None, "s", "anything")
    assert "search_news" in out  # points the model at the fallback tool


def test_registry_schemas_match_functions() -> None:
    assert set(tools.TOOLS) == {
        "get_price_history",
        "get_financials",
        "search_documents",
        "search_news",
        "compute_indicators",
        "extract_bulk",
    }
    for name, spec in tools.TOOLS.items():
        fn_schema = spec.schema["function"]
        assert fn_schema["name"] == name
        assert fn_schema["description"]
        assert fn_schema["parameters"]["type"] == "object"
        assert callable(spec.fn)
