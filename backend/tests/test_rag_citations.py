"""Tests for save-time citation rendering (rag/citations.py). SQLite-backed."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base
from app.models import DocumentChunk
from app.modules.ai.rag import citations


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    for i, url in ((1, "https://x/a"), (2, "https://x/b")):
        session.add(
            DocumentChunk(
                id=i,
                source_url=url,
                title=f"Article {i}",
                ticker="NVDA",
                chunk_index=0,
                content="body",
                embedding=[0.0] * 1536,
            )
        )
    session.commit()
    yield session
    session.close()


def test_format_sources_carries_tags() -> None:
    chunk = DocumentChunk(
        id=5,
        source_url="https://x/c",
        title="T",
        ticker="NVDA",
        chunk_index=0,
        content="Data-center revenue grew 40%.",
        embedding=[0.0] * 1536,
    )
    block = citations.format_sources([chunk])
    assert "[chunk:5]" in block and "https://x/c" in block


def test_cited_ids_order_and_dedupe() -> None:
    md = "A [chunk:2]. B [chunk:1]. A again [chunk:2]."
    assert citations.cited_ids(md) == [2, 1]


def test_invalid_ids_against_allowed_set(db_session) -> None:
    md = "claim [chunk:1] other [chunk:9]"
    assert citations.invalid_ids(db_session, md, allowed={1, 2}) == {9}


def test_invalid_ids_against_db_existence(db_session) -> None:
    md = "claim [chunk:2] fake [chunk:404]"
    assert citations.invalid_ids(db_session, md) == {404}


def test_render_links_numbers_and_sources_section(db_session) -> None:
    md = "Revenue grew [chunk:2]. Margins fell [chunk:1]. More on revenue [chunk:2]."
    out = citations.render(db_session, md, allowed={1, 2})
    assert "[[1]](https://x/b)" in out  # first-appearance numbering: chunk 2 -> [1]
    assert "[[2]](https://x/a)" in out
    assert "## Sources" in out
    assert "1. [Article 2](https://x/b)" in out
    assert "(chunk 2)" in out and "(chunk 1)" in out
    assert "[chunk:" not in out  # no raw tags survive


def test_render_strips_invalid_and_notes(db_session) -> None:
    md = "True claim [chunk:1]. Forged claim [chunk:999]."
    out = citations.render(db_session, md, allowed={1})
    assert "999" not in out
    assert "could not be verified" in out
    assert "[[1]](https://x/a)" in out  # the valid citation still renders


def test_render_styles_unverified_marker(db_session) -> None:
    out = citations.render(db_session, "Bold claim [unverified].")
    assert "⚠ unverified" in out
    assert "[unverified]" not in out


def test_render_without_tags_is_passthrough(db_session) -> None:
    md = "# Memo\n\nNo citations here."
    assert citations.render(db_session, md) == md  # no Sources section, no note
