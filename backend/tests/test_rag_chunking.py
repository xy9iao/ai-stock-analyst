"""Tests for the RAG chunking function (rag/chunking.py). Pure, deterministic.

These are the executable spec for the core chunking unit.
"""

import pytest

from app.modules.ai.rag.chunking import CHUNK_OVERLAP, CHUNK_SIZE, chunk_text

SENTENCE = "NVDA data-center revenue grew 40% year-over-year to $1,234.56 billion in Q2. "
LONG_TEXT = SENTENCE * 60  # ~4700 chars -> several chunks


def test_empty_and_whitespace_yield_no_chunks() -> None:
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_short_text_is_one_chunk() -> None:
    assert chunk_text("A short breaking-news item.") == ["A short breaking-news item."]


def test_deterministic() -> None:
    assert chunk_text(LONG_TEXT) == chunk_text(LONG_TEXT)


def test_chunks_respect_size_bound() -> None:
    assert all(len(c) <= CHUNK_SIZE for c in chunk_text(LONG_TEXT))


def test_covers_both_ends() -> None:
    chunks = chunk_text(LONG_TEXT)
    assert len(chunks) >= 2
    assert LONG_TEXT.strip().startswith(chunks[0][:80])
    assert LONG_TEXT.strip().endswith(chunks[-1][-80:])


def test_every_chunk_is_verbatim_source_text() -> None:
    # Citations show chunk content to a human — the chunker must never rewrite it.
    for chunk in chunk_text(LONG_TEXT):
        assert chunk in LONG_TEXT


def test_consecutive_chunks_overlap() -> None:
    chunks = chunk_text(LONG_TEXT)
    for left, right in zip(chunks, chunks[1:]):
        assert right[:50] in left  # the overlap region exists in both neighbors


def test_snaps_to_sentence_boundaries() -> None:
    # Sentence-rich text: every non-final chunk should end at a sentence end,
    # never mid-word or mid-number.
    chunks = chunk_text(LONG_TEXT)
    for chunk in chunks[:-1]:
        assert chunk.rstrip().endswith((".", "!", "?"))


def test_numbers_survive_chunking_intact() -> None:
    # The finance-specific failure mode: "$1,234.5|6 billion" must never happen.
    chunks = chunk_text(LONG_TEXT)
    occurrences = sum(chunk.count("$1,234.56 billion") for chunk in chunks)
    assert occurrences >= LONG_TEXT.count("$1,234.56 billion")


def test_pathological_unbroken_text_still_progresses() -> None:
    # No whitespace at all: hard cuts are allowed, infinite loops are not.
    text = "x" * (CHUNK_SIZE * 3)
    chunks = chunk_text(text)
    assert all(len(c) <= CHUNK_SIZE for c in chunks)
    assert sum(len(c) for c in chunks) >= len(text)  # overlap duplicates, never loses


def test_invalid_parameters_raise() -> None:
    with pytest.raises(ValueError):
        chunk_text("some text", size=CHUNK_OVERLAP, overlap=CHUNK_OVERLAP)
