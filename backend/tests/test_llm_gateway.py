"""Tests for the llm_client gateway's tool-calling entry (chat_message).

The provider is faked by monkeypatching `llm_client._client`; a standalone
in-memory SQLite session backs the llm_calls recording tests.
"""

from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  -- registers every model on Base.metadata
from app.core.config import settings
from app.core.database import Base
from app.core.errors import AppError
from app.models import LlmCall
from app.modules.ai import llm_client


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _response(
    content: str | None = "hi",
    tool_calls: list | None = None,
    cached_details: int | None = None,
    cache_hit_field: int | None = None,
):
    usage = SimpleNamespace(
        prompt_tokens=100,
        completion_tokens=20,
        prompt_tokens_details=(
            SimpleNamespace(cached_tokens=cached_details) if cached_details is not None else None
        ),
    )
    if cache_hit_field is not None:
        usage.prompt_cache_hit_tokens = cache_hit_field
    message = SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage)


class FakeProvider:
    def __init__(self, response) -> None:
        self.response = response
        self.kwargs: dict | None = None
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.kwargs = kwargs
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def _install(monkeypatch: pytest.MonkeyPatch, response) -> FakeProvider:
    fake = FakeProvider(response)
    monkeypatch.setattr(llm_client, "_client", lambda: fake)
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    return fake


def test_returns_full_message_and_passes_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = [SimpleNamespace(id="c1")]
    fake = _install(monkeypatch, _response(content=None, tool_calls=calls))
    schemas = [{"type": "function", "function": {"name": "t"}}]

    msg = llm_client.chat_message([{"role": "user", "content": "q"}], tools=schemas)

    assert msg.tool_calls == calls  # full message out, not a string
    assert fake.kwargs["tools"] == schemas  # tools reached the provider


def test_omits_tools_param_when_not_given(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _install(monkeypatch, _response())
    llm_client.chat_message([{"role": "user", "content": "q"}])
    assert "tools" not in fake.kwargs  # omitted entirely, not tools=None


def test_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "")
    with pytest.raises(AppError) as err:
        llm_client.chat_message([{"role": "user", "content": "q"}])
    assert err.value.status_code == 503


def test_demo_switch_off_blocks(monkeypatch: pytest.MonkeyPatch, db_session) -> None:
    _install(monkeypatch, _response())
    monkeypatch.setattr(settings, "demo_mode", True)
    with pytest.raises(AppError) as err:
        llm_client.chat_message([{"role": "user", "content": "q"}], db=db_session)
    assert err.value.code == "llm_disabled"


def test_provider_error_wrapped_as_apperror(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, RuntimeError("boom"))
    with pytest.raises(AppError) as err:
        llm_client.chat_message([{"role": "user", "content": "q"}])
    assert err.value.status_code == 502


def test_records_llm_call_with_cached_tokens_route_step(
    monkeypatch: pytest.MonkeyPatch, db_session
) -> None:
    _install(monkeypatch, _response(cached_details=64))

    llm_client.chat_message(
        [{"role": "user", "content": "q"}],
        db=db_session,
        session_id="sess-1",
        kind="research",
        route="agent",
        step=3,
    )

    row = db_session.query(LlmCall).one()
    assert row.cached_tokens == 64  # portable OpenAI field
    assert row.route == "agent" and row.steps == 3
    assert row.kind == "research" and row.session_id == "sess-1"
    assert row.prompt_tokens == 100 and row.completion_tokens == 20


def test_cached_tokens_deepseek_fallback_field(monkeypatch: pytest.MonkeyPatch, db_session) -> None:
    # No prompt_tokens_details -> fall back to DeepSeek's prompt_cache_hit_tokens.
    _install(monkeypatch, _response(cached_details=None, cache_hit_field=48))
    llm_client.chat_message([{"role": "user", "content": "q"}], db=db_session)
    assert db_session.query(LlmCall).one().cached_tokens == 48


def test_chat_still_returns_plain_text(monkeypatch: pytest.MonkeyPatch) -> None:
    # chat() keeps its old contract after the refactor: text out, one shared core.
    _install(monkeypatch, _response(content="plain answer"))
    assert llm_client.chat([{"role": "user", "content": "q"}]) == "plain answer"
