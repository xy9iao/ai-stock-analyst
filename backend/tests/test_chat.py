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
