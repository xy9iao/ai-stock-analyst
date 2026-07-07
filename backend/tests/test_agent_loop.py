"""Scaffolded tests for the owner-written loop (PR-2). Start all-red; implement
until green, one test at a time — they encode the D1–D7 decisions as a spec.

The gateway is faked by monkeypatching `llm_client.chat_message`, so write the
loop calling it module-attribute style (`llm_client.chat_message(...)`), matching
the repo idiom — a `from ... import chat_message` binding would dodge the patch.
"""

import json
from types import SimpleNamespace

import pytest

from app.core.errors import AppError
from app.modules.ai import llm_client
from app.modules.ai.agent import loop, tools


def _tool_call(call_id: str, name: str, arguments: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id, type="function", function=SimpleNamespace(name=name, arguments=arguments)
    )


def _assistant(content: str | None = None, tool_calls: list | None = None) -> SimpleNamespace:
    return SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls or None)


class FakeGateway:
    """Feeds scripted assistant messages and records every call's args."""

    def __init__(self, script: list[SimpleNamespace]) -> None:
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, messages, **kwargs):
        # Record a snapshot: the messages list at call time + the kwargs.
        self.calls.append({"messages": list(messages), "kwargs": kwargs})
        return self.script.pop(0)


# --- _execute_tool_call (D5: errors are data, never raised) ---


def test_execute_tool_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(
        tools.TOOLS,
        "get_financials",
        tools.ToolSpec(
            lambda db, session_id, ticker: f"{ticker} ok", tools.TOOLS["get_financials"].schema
        ),
    )
    call = _tool_call("c1", "get_financials", json.dumps({"ticker": "NVDA"}))
    assert loop._execute_tool_call(None, "s", call) == "NVDA ok"


def test_execute_tool_unknown_name_lists_valid_tools() -> None:
    call = _tool_call("c1", "get_weather", "{}")
    out = loop._execute_tool_call(None, "s", call)
    assert out.startswith("Error") and "get_price_history" in out


def test_execute_tool_malformed_arguments() -> None:
    call = _tool_call("c1", "get_financials", "{not json")
    out = loop._execute_tool_call(None, "s", call)
    assert out.startswith("Error") and "argument" in out.lower()


def test_execute_tool_apperror_message_fed_back(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(db, session_id, ticker):
        raise AppError("ticker_not_found", "No data for NOPE", 404)

    monkeypatch.setitem(
        tools.TOOLS, "get_financials", tools.ToolSpec(boom, tools.TOOLS["get_financials"].schema)
    )
    call = _tool_call("c1", "get_financials", json.dumps({"ticker": "NOPE"}))
    out = loop._execute_tool_call(None, "s", call)
    assert out.startswith("Error") and "No data for NOPE" in out


def test_execute_tool_unexpected_exception_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(db, session_id, ticker):
        raise RuntimeError("kaboom")

    monkeypatch.setitem(
        tools.TOOLS, "get_financials", tools.ToolSpec(boom, tools.TOOLS["get_financials"].schema)
    )
    call = _tool_call("c1", "get_financials", json.dumps({"ticker": "NVDA"}))
    out = loop._execute_tool_call(None, "s", call)
    assert out.startswith("Error")


# --- run_research (the loop itself) ---


def test_natural_exit_returns_memo_and_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeGateway([_assistant(content="# Memo\nDone.")])
    monkeypatch.setattr(llm_client, "chat_message", fake)

    result = loop.run_research(None, "sess", "why did NVDA drop?")
    assert result.memo == "# Memo\nDone."
    assert result.steps == 1
    assert result.step_limit_hit is False

    first_call = fake.calls[0]
    messages = first_call["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == loop.SYSTEM_PROMPT  # static, byte-stable prefix
    assert any("NVDA" in str(m.get("content")) for m in messages if m["role"] == "user")
    # D7: route/step attribution on every gateway call
    assert first_call["kwargs"].get("route") == "agent"
    assert first_call["kwargs"].get("step") == 1
    # tools offered on normal steps
    assert first_call["kwargs"].get("tools")


def test_parallel_batch_bookkeeping(monkeypatch: pytest.MonkeyPatch) -> None:
    batch = _assistant(
        tool_calls=[
            _tool_call("id_a", "get_financials", json.dumps({"ticker": "NVDA"})),
            _tool_call("id_b", "get_weather", "{}"),  # unknown tool -> error-as-data
        ]
    )
    fake = FakeGateway([batch, _assistant(content="memo")])
    monkeypatch.setattr(llm_client, "chat_message", fake)
    monkeypatch.setitem(
        tools.TOOLS,
        "get_financials",
        tools.ToolSpec(
            lambda db, session_id, ticker: "fin ok", tools.TOOLS["get_financials"].schema
        ),
    )

    result = loop.run_research(None, "sess", "compare")
    assert result.steps == 2 and result.step_limit_hit is False

    # Inspect the messages as seen by the SECOND gateway call:
    messages = fake.calls[1]["messages"]
    # D4: the assistant turn is appended BEFORE its tool results...
    roles = [m["role"] if isinstance(m, dict) else getattr(m, "role", "?") for m in messages]
    assistant_idx = roles.index("assistant")
    assert roles[assistant_idx + 1] == "tool" and roles[assistant_idx + 2] == "tool"
    # ...with exactly one tool message per tool_call_id, in batch order:
    tool_msgs = [m for m in messages if isinstance(m, dict) and m.get("role") == "tool"]
    assert [m["tool_call_id"] for m in tool_msgs] == ["id_a", "id_b"]
    assert tool_msgs[0]["content"] == "fin ok"
    assert tool_msgs[1]["content"].startswith("Error")  # D5: fed back, loop continued


def test_step_limit_forces_final_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    endless = _assistant(
        tool_calls=[_tool_call("x", "get_financials", json.dumps({"ticker": "NVDA"}))]
    )
    # More tool-hungry turns than the budget allows, then the forced answer.
    fake = FakeGateway([endless] * (loop.MAX_STEPS - 1) + [_assistant(content="partial memo")])
    monkeypatch.setattr(llm_client, "chat_message", fake)
    monkeypatch.setitem(
        tools.TOOLS,
        "get_financials",
        tools.ToolSpec(lambda db, session_id, ticker: "data", tools.TOOLS["get_financials"].schema),
    )

    result = loop.run_research(None, "sess", "q")
    # D2: the budget bounds TOTAL gateway calls, forced answer included.
    assert result.steps == loop.MAX_STEPS
    assert result.step_limit_hit is True
    assert "partial memo" in result.memo
    assert "step limit" in result.memo.lower()  # D3: explicit note in the memo

    # D3: the forced final call must OMIT tools (mechanism, not instruction).
    final_kwargs = fake.calls[-1]["kwargs"]
    assert not final_kwargs.get("tools")
    # Every prior call offered tools.
    assert all(c["kwargs"].get("tools") for c in fake.calls[:-1])
