"""Tests for the ingestion pipeline (rag/ingest.py). Network and embeddings faked."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base
from app.models import DocumentChunk
from app.modules.ai.rag import ingest
from app.modules.news.schemas import CompanyNews, NewsItem


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _news(*items: NewsItem) -> CompanyNews:
    return CompanyNews(ticker="NVDA", items=list(items))


def _item(url: str | None, headline: str = "NVDA news") -> NewsItem:
    return NewsItem(
        headline=headline,
        url=url,
        published_at=datetime(2026, 7, 20, tzinfo=timezone.utc),
    )


@pytest.fixture
def faked(monkeypatch: pytest.MonkeyPatch):
    bodies = {"https://a": "First sentence. " * 40, "https://b": "Other text. " * 40}
    monkeypatch.setattr(
        ingest.news_service,
        "get_company_news",
        lambda db, ticker: _news(_item("https://a"), _item("https://b")),
    )
    monkeypatch.setattr(ingest, "_fetch_body", lambda url: bodies.get(url))
    monkeypatch.setattr(ingest, "embed_texts", lambda texts, db=None: [[0.0] * 1536 for _ in texts])
    return bodies


def test_ingests_all_reachable_docs(db_session, faked) -> None:
    stats = ingest.ingest_ticker(db_session, "nvda")
    assert stats.ticker == "NVDA"
    assert stats.docs_ingested == 2
    assert stats.docs_skipped == 0
    rows = db_session.scalars(select(DocumentChunk)).all()
    assert len(rows) == stats.chunks_written > 0
    assert {r.source_url for r in rows} == {"https://a", "https://b"}
    assert all(r.ticker == "NVDA" for r in rows)


def test_skips_missing_url_and_dead_fetch(db_session, faked, monkeypatch) -> None:
    monkeypatch.setattr(
        ingest.news_service,
        "get_company_news",
        lambda db, ticker: _news(_item(None), _item("https://dead"), _item("https://a")),
    )
    stats = ingest.ingest_ticker(db_session, "NVDA")
    assert stats.docs_ingested == 1
    assert stats.docs_skipped == 2


def test_reingest_replaces_chunks_not_duplicates(db_session, faked) -> None:
    ingest.ingest_ticker(db_session, "NVDA")
    first_count = len(db_session.scalars(select(DocumentChunk)).all())
    ingest.ingest_ticker(db_session, "NVDA")
    assert len(db_session.scalars(select(DocumentChunk)).all()) == first_count


def test_chunk_indexes_are_sequential_per_doc(db_session, faked) -> None:
    ingest.ingest_ticker(db_session, "NVDA")
    rows = db_session.scalars(
        select(DocumentChunk).where(DocumentChunk.source_url == "https://a")
    ).all()
    assert sorted(r.chunk_index for r in rows) == list(range(len(rows)))
