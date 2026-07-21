"""Tests for the chat API. The LLM and context assembly are mocked (no network/cost)."""

import pytest
from fastapi.testclient import TestClient

from app.modules.ai import llm_client
from app.modules.chat import context as chat_context


class _Recorder:
    def __init__(self) -> None:
        self.last_messages: list[dict] | None = None
        self.last_options = None


@pytest.fixture
def fake_chat(monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    rec = _Recorder()

    def _llm(messages, **kw):
        rec.last_messages = messages
        return "Mock reply."

    def _ctx(db, options, session_id):
        rec.last_options = options
        return "CTX" if (options.include_holdings or options.ticker) else ""

    monkeypatch.setattr(llm_client, "chat", _llm)
    monkeypatch.setattr(chat_context, "build_context", _ctx)
    return rec


def test_new_session_message(client: TestClient, fake_chat: _Recorder) -> None:
    res = client.post("/api/chat/messages", json={"message": "Is NVDA a buy?"})
    assert res.status_code == 201
    body = res.json()
    assert body["session_id"] >= 1
    assert body["reply"] == "Mock reply."

    msgs = client.get(f"/api/chat/sessions/{body['session_id']}/messages").json()
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[0]["content"] == "Is NVDA a buy?"


def test_existing_session_keeps_history(client: TestClient, fake_chat: _Recorder) -> None:
    sid = client.post("/api/chat/messages", json={"message": "Hi"}).json()["session_id"]
    client.post("/api/chat/messages", json={"session_id": sid, "message": "Second"})

    msgs = client.get(f"/api/chat/sessions/{sid}/messages").json()
    assert len(msgs) == 4  # user/assistant x2
    # the second LLM call included the prior turn as history
    seen = [(m["role"], m["content"]) for m in fake_chat.last_messages]
    assert ("user", "Hi") in seen


def test_post_unknown_session_404(client: TestClient, fake_chat: _Recorder) -> None:
    res = client.post("/api/chat/messages", json={"session_id": 9999, "message": "x"})
    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "chat_session_not_found"


def test_list_sessions(client: TestClient, fake_chat: _Recorder) -> None:
    client.post("/api/chat/messages", json={"message": "A"})
    res = client.get("/api/chat/sessions")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_messages_missing_session_404(client: TestClient, fake_chat: _Recorder) -> None:
    assert client.get("/api/chat/sessions/9999/messages").status_code == 404


def test_context_toggles_passed_through(client: TestClient, fake_chat: _Recorder) -> None:
    client.post(
        "/api/chat/messages",
        json={"message": "x", "context": {"include_holdings": True, "ticker": "nvda"}},
    )
    assert fake_chat.last_options.include_holdings is True
    assert fake_chat.last_options.ticker == "nvda"


def test_empty_message_rejected_422(client: TestClient, fake_chat: _Recorder) -> None:
    assert client.post("/api/chat/messages", json={"message": ""}).status_code == 422


def test_long_history_compresses_and_persists_summary(
    client: TestClient, fake_chat: _Recorder, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.core.config import settings
    from app.modules.chat import compression

    monkeypatch.setattr(settings, "chat_compress_threshold_tokens", 10)
    monkeypatch.setattr(settings, "chat_verbatim_messages", 2)
    monkeypatch.setattr(
        compression.llm_client, "complete", lambda system, user, **kw: "SUMMARY OF OLD TURNS"
    )

    first = client.post("/api/chat/messages", json={"message": "tell me about NVDA " * 20})
    session_id = first.json()["session_id"]
    client.post(
        "/api/chat/messages",
        json={"message": "what about MSFT? " * 20, "session_id": session_id},
    )
    # By the third message, four stored messages exceed the 2-message window ->
    # the older pair gets evicted into the summary.
    client.post("/api/chat/messages", json={"message": "and AMD?", "session_id": session_id})

    roles = [(m["role"], m["content"]) for m in fake_chat.last_messages]
    summary_blocks = [c for r, c in roles if r == "system" and "summary" in c.lower()]
    assert summary_blocks and "SUMMARY OF OLD TURNS" in summary_blocks[0]
    # summary system block comes before the verbatim history (cache ordering)
    summary_idx = next(i for i, (r, c) in enumerate(roles) if "SUMMARY OF OLD" in c)
    first_history_idx = next(i for i, (r, c) in enumerate(roles) if r in ("user", "assistant"))
    assert summary_idx < first_history_idx


def test_compression_failure_degrades_to_cap(
    client: TestClient, fake_chat: _Recorder, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.core.config import settings
    from app.core.errors import AppError
    from app.modules.chat import compression

    monkeypatch.setattr(settings, "chat_compress_threshold_tokens", 10)

    def boom(db, sid, summary, history):
        raise AppError("llm_error", "down", 502)

    monkeypatch.setattr(compression, "compress", boom)

    res = client.post("/api/chat/messages", json={"message": "long question " * 30})
    assert res.status_code == 201  # chat survives; capped history was used
    assert fake_chat.last_messages is not None


def test_eviction_cursor_prevents_resummarizing(
    client: TestClient, fake_chat: _Recorder, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The measurement-discovered bug: without the cursor, every event re-fed
    already-summarized turns into the summarizer (quadratic, drifty)."""
    from app.core.config import settings
    from app.modules.chat import compression

    monkeypatch.setattr(settings, "chat_compress_threshold_tokens", 10)
    monkeypatch.setattr(settings, "chat_verbatim_messages", 2)
    payloads: list[str] = []

    def fake_complete(system, user, **kw):
        payloads.append(user)
        return "SUMMARY"

    monkeypatch.setattr(compression.llm_client, "complete", fake_complete)

    sid = client.post("/api/chat/messages", json={"message": "FIRST-QUESTION " * 10}).json()[
        "session_id"
    ]
    for text in ("SECOND-QUESTION " * 10, "THIRD-QUESTION " * 10, "FOURTH-QUESTION " * 10):
        client.post("/api/chat/messages", json={"message": text, "session_id": sid})

    assert len(payloads) >= 2  # multiple compression events fired
    # A later event must never re-summarize turns already behind the cursor.
    assert "FIRST-QUESTION" not in payloads[-1]
    # And evicted turns never reappear in the chat prompt itself.
    prompt_text = " ".join(m["content"] for m in fake_chat.last_messages)
    assert "FIRST-QUESTION" not in prompt_text.replace("SUMMARY", "")
