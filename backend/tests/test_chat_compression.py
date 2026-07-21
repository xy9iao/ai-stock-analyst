"""Tests for chat compression (chat/compression.py). LLM mocked — deterministic.

Executable spec for the core unit: token estimation, the trigger, and the
batch-eviction compress step.
"""

import pytest

from app.core.config import settings
from app.core.errors import AppError
from app.modules.chat import compression


def _msg(role: str, content: str) -> dict:
    return {"role": role, "content": content}


def _history(n: int, chars_each: int = 100) -> list[dict]:
    return [_msg("user" if i % 2 == 0 else "assistant", "x" * chars_each) for i in range(n)]


@pytest.fixture
def fake_llm(monkeypatch: pytest.MonkeyPatch):
    seen: dict = {}

    def fake_complete(system, user, **kw):
        seen.update(kw, system=system, user=user)
        return "NEW SUMMARY"

    monkeypatch.setattr(compression.llm_client, "complete", fake_complete)
    return seen


def test_estimate_tokens_chars_over_four() -> None:
    msgs = [_msg("user", "a" * 400), _msg("assistant", "b" * 200)]
    assert compression.estimate_tokens(msgs) == 150


def test_needs_compression_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "chat_compress_threshold_tokens", 100)
    assert not compression.needs_compression([_msg("user", "x" * 400)])  # exactly 100
    assert compression.needs_compression([_msg("user", "x" * 404)])  # 101


def test_compress_evicts_all_but_last_n(monkeypatch: pytest.MonkeyPatch, fake_llm) -> None:
    monkeypatch.setattr(settings, "chat_verbatim_messages", 4)
    history = _history(10)
    summary, kept = compression.compress(None, "sess", None, history)
    assert summary == "NEW SUMMARY"
    assert kept == history[-4:]  # verbatim window untouched, order preserved


def test_compress_payload_has_evicted_and_prior_summary_only(
    monkeypatch: pytest.MonkeyPatch, fake_llm
) -> None:
    monkeypatch.setattr(settings, "chat_verbatim_messages", 2)
    history = [
        _msg("user", "EVICTED-OLD"),
        _msg("assistant", "EVICTED-MID"),
        _msg("user", "KEPT-A"),
        _msg("assistant", "KEPT-B"),
    ]
    compression.compress(None, "sess", "PRIOR SUMMARY", history)
    assert "PRIOR SUMMARY" in fake_llm["user"]
    assert "EVICTED-OLD" in fake_llm["user"] and "EVICTED-MID" in fake_llm["user"]
    assert "KEPT-A" not in fake_llm["user"]  # the window is never re-summarized


def test_compress_short_history_is_noop(monkeypatch: pytest.MonkeyPatch, fake_llm) -> None:
    monkeypatch.setattr(settings, "chat_verbatim_messages", 12)
    history = _history(4)
    summary, kept = compression.compress(None, "sess", "OLD", history)
    assert summary == "OLD" and kept == history
    assert "user" not in fake_llm  # no LLM call spent


def test_compress_routes_through_gateway_as_summarize(
    monkeypatch: pytest.MonkeyPatch, fake_llm
) -> None:
    monkeypatch.setattr(settings, "chat_verbatim_messages", 2)
    compression.compress(None, "demo-1", None, _history(6))
    assert fake_llm["kind"] == "summarize"
    assert fake_llm["session_id"] == "demo-1"
    assert fake_llm["temperature"] <= 0.3  # summaries should not be creative


def test_compress_failure_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(system, user, **kw):
        raise AppError("llm_error", "down", 502)

    monkeypatch.setattr(compression.llm_client, "complete", boom)
    monkeypatch.setattr(settings, "chat_verbatim_messages", 2)
    with pytest.raises(AppError):
        compression.compress(None, "sess", None, _history(6))  # service owns the fallback
