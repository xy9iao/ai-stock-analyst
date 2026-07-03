"""Tests for the public-demo hardening: anonymous session isolation, the
per-session cost caps, the LLM master switch, /api/stats, and session reset.

Demo mode is toggled per-test by monkeypatching the settings object (all code
reads settings at call time). Visitors are simulated with explicit cookies.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.demo_session import SESSION_COOKIE
from app.modules.ai import context, llm_client


@pytest.fixture
def demo_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "demo_mode", True)


@pytest.fixture
def fake_report_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_client, "complete", lambda system, user, **kw: "# Mock report")
    monkeypatch.setattr(context, "build_single_stock_context", lambda db, ticker, session_id: "ctx")
    monkeypatch.setattr(context, "build_portfolio_context", lambda db, session_id: "ctx")


def _holding_payload() -> dict:
    return {"ticker": "NVDA", "shares": "1", "average_cost": "100"}


def test_demo_sessions_are_isolated(client: TestClient, demo_mode: None) -> None:
    client.cookies.set(SESSION_COOKIE, "visitor-a")
    created = client.post("/api/holdings", json=_holding_payload())
    assert created.status_code == 201
    holding_id = created.json()["id"]
    assert len(client.get("/api/holdings").json()) == 1

    client.cookies.set(SESSION_COOKIE, "visitor-b")
    assert client.get("/api/holdings").json() == []  # B sees nothing of A's
    assert client.get(f"/api/holdings/{holding_id}").status_code == 404
    assert client.delete(f"/api/holdings/{holding_id}").status_code == 404


def test_demo_cookie_issued_on_first_visit(client: TestClient, demo_mode: None) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    assert SESSION_COOKIE in res.cookies
    assert res.cookies[SESSION_COOKIE] != "local"


def test_local_mode_uses_shared_bucket(client: TestClient) -> None:
    # demo_mode off (default): no cookie is issued; data lands in "local".
    res = client.post("/api/holdings", json=_holding_payload())
    assert res.status_code == 201
    assert SESSION_COOKIE not in res.cookies
    assert len(client.get("/api/holdings").json()) == 1


def test_demo_report_cap(
    client: TestClient, demo_mode: None, fake_report_llm: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "demo_report_limit", 2)
    client.cookies.set(SESSION_COOKIE, "visitor-a")
    for _ in range(2):
        assert client.post("/api/reports", json={"report_type": "portfolio"}).status_code == 201
    res = client.post("/api/reports", json={"report_type": "portfolio"})
    assert res.status_code == 429
    assert res.json()["detail"]["code"] == "demo_report_limit"

    # A different visitor still has their own quota.
    client.cookies.set(SESSION_COOKIE, "visitor-b")
    assert client.post("/api/reports", json={"report_type": "portfolio"}).status_code == 201


def test_llm_switch_default_off_blocks_demo_chat(
    client: TestClient, demo_mode: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    res = client.post("/api/chat/messages", json={"message": "hi"})
    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "llm_disabled"


def test_admin_switch_requires_token(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "admin_token", "secret")
    body = {"enabled": True}
    assert client.post("/api/admin/llm", json=body).status_code == 403
    assert (
        client.post("/api/admin/llm", json=body, headers={"X-Admin-Token": "wrong"}).status_code
        == 403
    )
    ok = client.post("/api/admin/llm", json=body, headers={"X-Admin-Token": "secret"})
    assert ok.status_code == 200
    assert ok.json()["enabled"] is True
    assert ok.json()["enabled_until"] is not None

    status = client.get("/api/admin/llm", headers={"X-Admin-Token": "secret"})
    assert status.json()["enabled"] is True


def test_admin_switch_forbidden_when_no_token_configured(client: TestClient) -> None:
    # With ADMIN_TOKEN unset the endpoint can never be used (fail closed).
    res = client.post("/api/admin/llm", json={"enabled": True}, headers={"X-Admin-Token": ""})
    assert res.status_code == 403


def test_llm_calls_recorded_and_stats(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # Exercise the real gateway with a faked OpenAI client (no network).
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    response = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
        choices=[SimpleNamespace(message=SimpleNamespace(content="Mock reply."))],
    )
    fake_openai = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: response))
    )
    monkeypatch.setattr(llm_client, "_client", lambda: fake_openai)

    res = client.post("/api/chat/messages", json={"message": "hi"})
    assert res.status_code == 201

    stats = client.get("/api/stats").json()
    assert stats["total_calls"] == 1
    assert stats["total_prompt_tokens"] == 10
    assert stats["total_completion_tokens"] == 5
    assert stats["by_kind"][0]["kind"] == "chat"


def test_session_reset_clears_cookie(client: TestClient) -> None:
    res = client.post("/api/session/reset")
    assert res.status_code == 204
    assert 'session_id=""' in res.headers.get("set-cookie", "")
