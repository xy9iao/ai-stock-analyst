"""The Research Agent's tool layer: six read-only tools.

Each tool is a thin wrapper over an existing service-layer function (never a
provider or repository directly), so cache-aside, ticker normalization, and
AppError semantics are inherited for free. Every tool returns a compact,
LLM-ready string — tools are the model's eyes, so outputs are kept small on
purpose (token cost is paid on every remaining loop step).

`TOOLS` maps tool name -> (callable, OpenAI-format schema). The loop binds
`db` and `session_id` and passes the model's arguments as keywords; schemas
mirror the docstrings. Phase 13 locked five tools; Phase 14 added
`search_documents` (hybrid retrieval over ingested article bodies) as a
recorded scope decision. Do not add tools mid-phase.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.modules.ai import llm_client
from app.modules.ai.rag import retrieval
from app.modules.financials import service as financials_service
from app.modules.market_data import service as market_service
from app.modules.market_data.schemas import HistoryRange
from app.modules.news import service as news_service

from . import indicators as ind

_MAX_NEWS_LIMIT = 10
_MAX_PASSAGE_CHARS = 600  # tool outputs are resent every remaining loop step
_MAX_EXTRACT_TEXTS = 20
_MAX_EXTRACT_CHARS = 8000
_HISTORY_SAMPLE_POINTS = 15

_EXTRACT_SYSTEM = (
    "You extract facts. From the provided texts, list the concrete facts relevant "
    "to the stated focus as short bullet points. No opinions, no advice, no filler; "
    "keep numbers and dates exact; answer with bullets only."
)


def get_price_history(db: Session, session_id: str, ticker: str, period: str = "1m") -> str:
    """Price/volume history for a ticker over 1d, 1w, 1m, or 1y.

    Returns a compact summary (change over the period, high/low) plus up to 15
    sampled closes, oldest first.
    """
    try:
        history_range = HistoryRange(period)
    except ValueError:
        return f"Invalid period '{period}'. Valid periods: 1d, 1w, 1m, 1y."
    history = market_service.get_price_history(db, ticker, history_range)
    candles = history.candles
    if not candles:
        return f"No price data available for {history.ticker} over {period}."

    first, last = candles[0], candles[-1]
    change_pct = (
        (float(last.close) - float(first.close)) / float(first.close) * 100
        if float(first.close)
        else 0.0
    )
    high = max(float(c.high) for c in candles)
    low = min(float(c.low) for c in candles)
    lines = [
        f"{history.ticker} {period}: close {first.close} -> {last.close} "
        f"({change_pct:+.2f}%), high {high:.2f}, low {low:.2f}, {len(candles)} candles."
    ]
    step = max(1, len(candles) // _HISTORY_SAMPLE_POINTS)
    for candle in candles[::step][-_HISTORY_SAMPLE_POINTS:]:
        date = str(candle.timestamp)[:10]
        lines.append(f"- {date}: close {candle.close}, volume {candle.volume}")
    return "\n".join(lines)


def get_financials(db: Session, session_id: str, ticker: str) -> str:
    """Latest financial snapshot for a ticker: market cap, revenue (+growth),
    EPS, net income, margins, and earnings dates. Values may be missing."""
    snapshot = financials_service.get_snapshot(db, ticker)
    fields = [
        ("company", snapshot.company_name),
        ("sector", snapshot.sector),
        ("market cap", snapshot.market_cap),
        ("revenue", snapshot.revenue),
        ("revenue growth", snapshot.revenue_growth),
        ("EPS", snapshot.eps),
        ("net income", snapshot.net_income),
        ("gross margin", snapshot.gross_margin),
        ("operating margin", snapshot.operating_margin),
        ("last earnings", snapshot.last_earnings_date),
        ("next earnings", snapshot.next_earnings_date),
    ]
    parts = [f"{label}: {value}" for label, value in fields if value is not None]
    if not parts:
        return f"No financial data available for {snapshot.ticker}."
    return f"{snapshot.ticker} financials — " + "; ".join(str(p) for p in parts)


def search_news(db: Session, session_id: str, ticker: str, query: str = "", limit: int = 5) -> str:
    """Recent company news headlines for a ticker, newest first. Optional
    `query` filters headlines/summaries by substring; `limit` caps results (max 10)."""
    news = news_service.get_company_news(db, ticker)
    items = news.items
    if query:
        needle = query.lower()
        items = [
            item
            for item in items
            if needle in item.headline.lower() or needle in (item.summary or "").lower()
        ]
    items = items[: max(1, min(limit, _MAX_NEWS_LIMIT))]
    if not items:
        return f"No news found for {news.ticker}" + (f" matching '{query}'." if query else ".")
    lines = [f"News for {news.ticker}" + (f" matching '{query}':" if query else ":")]
    for i, item in enumerate(items, 1):
        date = str(item.published_at)[:10] if item.published_at else "n.d."
        source = item.source or "unknown"
        line = f"[{i}] {item.headline} ({source}, {date})"
        if item.summary:
            line += f" — {item.summary[:200]}"
        lines.append(line)
    return "\n".join(lines)


def compute_indicators(
    db: Session, session_id: str, ticker: str, indicators: list[str] | None = None
) -> str:
    """Technical indicators from 1y of daily closes. Supported: sma20, sma50,
    ema12, ema26, rsi14. Defaults to all five when `indicators` is omitted."""
    supported: dict[str, Callable[[list[float]], float | None]] = {
        "sma20": lambda closes: ind.sma(closes, 20),
        "sma50": lambda closes: ind.sma(closes, 50),
        "ema12": lambda closes: ind.ema(closes, 12),
        "ema26": lambda closes: ind.ema(closes, 26),
        "rsi14": lambda closes: ind.rsi(closes, 14),
    }
    wanted = [name.lower() for name in (indicators or list(supported))]
    history = market_service.get_price_history(db, ticker, HistoryRange.ONE_YEAR)
    closes = [float(c.close) for c in history.candles]
    if not closes:
        return f"No price data available for {history.ticker}."
    parts: list[str] = []
    for name in wanted:
        fn = supported.get(name)
        if fn is None:
            parts.append(f"{name}: unsupported (valid: {', '.join(supported)})")
            continue
        value = fn(closes)
        parts.append(f"{name}: {value:.2f}" if value is not None else f"{name}: insufficient data")
    latest = closes[-1]
    return f"{history.ticker} indicators (latest close {latest:.2f}) — " + "; ".join(parts)


def extract_bulk(db: Session, session_id: str, texts: list[str], focus: str) -> str:
    """Distill a list of texts (headlines/summaries) into the concrete facts
    relevant to `focus`. Routes internally through the flash-tier LLM path."""
    if not texts:
        return "No texts provided."
    joined = "\n---\n".join(str(t) for t in texts[:_MAX_EXTRACT_TEXTS])[:_MAX_EXTRACT_CHARS]
    user = f"Focus: {focus}\n\nTexts:\n{joined}"
    return llm_client.complete(
        _EXTRACT_SYSTEM,
        user,
        temperature=0.2,
        db=db,
        session_id=session_id,
        kind="extract",
    )


def search_documents(db: Session, session_id: str, query: str, ticker: str = "") -> str:
    """Deep hybrid search (semantic + keyword) over ingested full article bodies.
    Returns the most relevant passages with stable [chunk:<id>] tags, title,
    date, and source URL — reference passages by their chunk tag."""
    chunks = retrieval.hybrid_search(db, query, ticker=ticker or None)
    if not chunks:
        return (
            f"No ingested documents matched '{query}'. The document corpus may not "
            "cover this topic yet — try search_news for headlines instead."
        )
    lines = [f"Passages matching '{query}':"]
    for chunk in chunks:
        date = str(chunk.published_at)[:10] if chunk.published_at else "n.d."
        lines.append(
            f"[chunk:{chunk.id}] {chunk.title} ({date}) {chunk.source_url}\n"
            f"{chunk.content[:_MAX_PASSAGE_CHARS]}"
        )
    return "\n\n".join(lines)


@dataclass(frozen=True)
class ToolSpec:
    fn: Callable[..., str]
    schema: dict[str, Any]


def _schema(name: str, description: str, params: dict[str, Any], required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": params, "required": required},
        },
    }


_TICKER = {"type": "string", "description": "Stock ticker symbol, e.g. NVDA or VFV.TO"}

TOOLS: dict[str, ToolSpec] = {
    "get_price_history": ToolSpec(
        get_price_history,
        _schema(
            "get_price_history",
            "Price/volume history for a ticker: period change, high/low, sampled closes.",
            {
                "ticker": _TICKER,
                "period": {
                    "type": "string",
                    "enum": ["1d", "1w", "1m", "1y"],
                    "description": "History window (default 1m)",
                },
            },
            ["ticker"],
        ),
    ),
    "get_financials": ToolSpec(
        get_financials,
        _schema(
            "get_financials",
            "Latest financial snapshot: market cap, revenue (+growth), EPS, margins, "
            "earnings dates.",
            {"ticker": _TICKER},
            ["ticker"],
        ),
    ),
    "search_documents": ToolSpec(
        search_documents,
        _schema(
            "search_documents",
            "Deep hybrid search (semantic + keyword) over ingested full article bodies; "
            "returns relevant passages with [chunk:<id>] tags and source URLs. Use for "
            "evidence beyond headlines.",
            {
                "query": {"type": "string", "description": "What to look for, natural language"},
                "ticker": {
                    "type": "string",
                    "description": "Optional ticker to restrict results to",
                },
            },
            ["query"],
        ),
    ),
    "search_news": ToolSpec(
        search_news,
        _schema(
            "search_news",
            "Recent company news headlines (newest first), optionally filtered by a "
            "substring query.",
            {
                "ticker": _TICKER,
                "query": {"type": "string", "description": "Optional substring filter"},
                "limit": {"type": "integer", "description": "Max results, 1-10 (default 5)"},
            },
            ["ticker"],
        ),
    ),
    "compute_indicators": ToolSpec(
        compute_indicators,
        _schema(
            "compute_indicators",
            "Technical indicators from 1y of daily closes: sma20, sma50, ema12, ema26, rsi14.",
            {
                "ticker": _TICKER,
                "indicators": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Subset of: sma20, sma50, ema12, ema26, rsi14 (default all)",
                },
            },
            ["ticker"],
        ),
    ),
    "extract_bulk": ToolSpec(
        extract_bulk,
        _schema(
            "extract_bulk",
            "Distill a list of texts into the concrete facts relevant to a focus (bulk reading).",
            {
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Texts to distill (max 20)",
                },
                "focus": {"type": "string", "description": "What facts to extract"},
            },
            ["texts", "focus"],
        ),
    ),
}
