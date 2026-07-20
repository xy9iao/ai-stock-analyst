"""Tests for hybrid retrieval (rag/retrieval.py).

The pure units (RRF, BM25 rescore) are tested directly; hybrid_search is
tested with the two DB pool functions monkeypatched — Postgres-specific SQL
(cosine distance, websearch_to_tsquery) is exercised live, not in unit tests.
"""

import pytest

from app.core.errors import AppError
from app.models import DocumentChunk
from app.modules.ai.rag import retrieval
from app.modules.ai.rag.retrieval import bm25_rescore, hybrid_search, rrf_fuse


def _chunk(chunk_id: int, content: str) -> DocumentChunk:
    return DocumentChunk(
        id=chunk_id,
        source_url=f"https://x/{chunk_id}",
        title="t",
        ticker="NVDA",
        chunk_index=0,
        content=content,
        embedding=[0.0] * 1536,
    )


# --- RRF ---


def test_rrf_known_math() -> None:
    # id 2 accumulates 1/61 + 1/62 — the highest combined score.
    assert rrf_fuse([[1, 2, 3], [2, 3, 1]]) == [2, 1, 3]


def test_rrf_present_in_both_beats_single_list_winner() -> None:
    assert rrf_fuse([[7, 1], [7, 2]])[0] == 7


def test_rrf_disjoint_lists_tie_break_deterministic() -> None:
    assert rrf_fuse([[4], [2]]) == [2, 4]  # equal scores -> lower id first


def test_rrf_single_list_passthrough() -> None:
    assert rrf_fuse([[3, 1, 2]]) == [3, 1, 2]


def test_rrf_empty() -> None:
    assert rrf_fuse([]) == []
    assert rrf_fuse([[], []]) == []


# --- BM25 rescore ---


def test_bm25_ranks_query_term_match_first() -> None:
    candidates = [
        _chunk(1, "nvidia revenue grew again revenue revenue revenue"),
        _chunk(2, "nvidia blackwell delay announced by the company"),
        _chunk(3, "the weather is nice today"),
    ]
    ranked = bm25_rescore("blackwell delay", candidates)
    assert ranked[0].id == 2


def test_bm25_no_term_overlap_keeps_fts_order() -> None:
    candidates = [_chunk(1, "alpha beta"), _chunk(2, "gamma delta")]
    ranked = bm25_rescore("unrelated words", candidates)
    assert [c.id for c in ranked] == [1, 2]  # all-zero scores -> stable FTS order


def test_bm25_empty_candidates() -> None:
    assert bm25_rescore("anything", []) == []


# --- hybrid_search composition ---


def test_hybrid_fuses_and_cuts_top_k(monkeypatch: pytest.MonkeyPatch) -> None:
    vec = [_chunk(i, f"v{i}") for i in (1, 2, 3)]
    lex = [_chunk(i, f"l{i}") for i in (2, 3, 4)]
    monkeypatch.setattr(retrieval, "_vector_pool", lambda db, q, t: vec)
    monkeypatch.setattr(retrieval, "_lexical_pool", lambda db, q, t: lex)

    result = hybrid_search(None, "q", top_k=2)
    # 2 (ranks 2+1) beats 3 (ranks 3+2); both beat 1, which is in one list only.
    assert [c.id for c in result] == [2, 3]
    assert len(result) == 2


def test_hybrid_vector_failure_degrades_to_lexical(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(db, q, t):
        raise AppError("embeddings_error", "down", 502)

    lex = [_chunk(9, "only lexical")]
    monkeypatch.setattr(retrieval, "_vector_pool", _boom)
    monkeypatch.setattr(retrieval, "_lexical_pool", lambda db, q, t: lex)

    result = hybrid_search(None, "q")
    assert [c.id for c in result] == [9]  # retrieval never takes the report down


def test_hybrid_empty_corpus_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retrieval, "_vector_pool", lambda db, q, t: [])
    monkeypatch.setattr(retrieval, "_lexical_pool", lambda db, q, t: [])
    assert hybrid_search(None, "q") == []
