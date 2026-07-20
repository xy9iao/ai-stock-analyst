"""Tests for the citation-case checker (eval/citation_check.py). SQLite-backed."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base
from app.models import DocumentChunk
from eval.citation_check import check_citation


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    session.add(
        DocumentChunk(
            id=1,
            source_url="https://x/a",
            title="T",
            ticker="AMD",
            chunk_index=0,
            content="AMD's Instinct GPUs are ramping in the data center.",
            embedding=[0.0] * 1536,
        )
    )
    session.add(
        DocumentChunk(
            id=2,
            source_url="https://x/b",
            title="T2",
            ticker="AMD",
            chunk_index=0,
            content="Completely unrelated content about weather.",
            embedding=[0.0] * 1536,
        )
    )
    session.commit()
    yield session
    session.close()


def test_pass_when_cited_and_supported(db_session) -> None:
    memo = "- Instinct GPU ramp is driving momentum [chunk:1].\n- Other line."
    result = check_citation(db_session, "c", memo, "Instinct")
    assert result.passed


def test_fail_when_atom_absent(db_session) -> None:
    result = check_citation(db_session, "c", "- Nothing relevant here.", "Instinct")
    assert not result.atom_found and not result.passed


def test_fail_when_uncited(db_session) -> None:
    result = check_citation(db_session, "c", "- Instinct ramp continues, no tag.", "Instinct")
    assert result.atom_found and not result.cited and not result.passed


def test_fail_when_cited_chunk_does_not_support(db_session) -> None:
    # The wrong-source case: true claim, citation points at an unrelated chunk.
    memo = "- Instinct ramp continues [chunk:2]."
    result = check_citation(db_session, "c", memo, "Instinct")
    assert result.cited and not result.supported and not result.passed


def test_any_supporting_tag_on_the_line_passes(db_session) -> None:
    memo = "- Instinct ramp continues [chunk:2] [chunk:1]."
    assert check_citation(db_session, "c", memo, "Instinct").passed


def test_matching_is_case_insensitive(db_session) -> None:
    memo = "- INSTINCT accelerators ramping [chunk:1]."
    assert check_citation(db_session, "c", memo, "instinct").passed
