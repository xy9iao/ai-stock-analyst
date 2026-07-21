"""The Research Agent's hand-written tool-use loop (ReAct-shaped).

Drives the tool-calling conversation shape:

    system -> user -> assistant(tool_calls) -> tool results (one per id) -> ... -> assistant(content)

Invariants: every LLM call goes through the llm_client gateway (this module never
instantiates a client); messages are append-only, so each step reuses the prior
prompt prefix (provider-side caching); errors inside tools come back as tool
results, never as raised exceptions; the step budget is the loop's own safety
rail on cost.
"""

import json
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.ai import llm_client
from app.modules.ai.agent.tools import TOOLS

MAX_STEPS = 8

# The static prefix: frozen at import, byte-stable across runs (no dates, no query
# text, no session data — per-run data rides in the user message). Together with the
# tool schemas this is the cacheable block the loop resends on every step.
SYSTEM_PROMPT = """You are an evidence-gathering research agent for a stock research app. \
You investigate open-ended market questions by pulling evidence with the provided \
read-only tools. You are NOT a licensed financial advisor and you do not give \
guaranteed financial advice.

Tool policy (always follow):
- Gather evidence with the tools BEFORE answering; investigate multiple angles when \
the question warrants it.
- Every number and factual claim must come from a tool result. If the tools did not \
return it, say it is unavailable — never fabricate or fill from memory.
- Tool errors are information: correct the arguments or try another tool rather than \
giving up.
- You have a hard budget of 8 steps. Plan evidence gathering to fit it: gather broadly \
early, and never re-query a tool with a rephrasing of a question it already answered — \
answer instead.

Output contract:
- Produce an evidence memo: findings first, each finding tied to the evidence that \
produced it (which data showed it).
- When search_documents passages support a key factual claim, attach that passage's \
[chunk:<id>] tag immediately after the claim. Cite only tags you actually saw in tool \
results — never invent one. Mark key claims no source supports with [unverified].
- End with what could not be verified, if anything.
- You deliver research findings, never trade instructions or action labels.

Safety boundary (always follow):
- Never use language like "guaranteed", "risk-free", "you must buy", or "this will \
definitely go up".
- Prefer "based on available data", "a reasonable action may be", "consider", "the risk is".
- End with a brief reminder that this is research, not financial advice, and the user \
is responsible for their own decisions.

Output GitHub-flavored Markdown only."""


@dataclass(frozen=True)
class ResearchResult:
    """What a research run produces (consumed by report_generator in PR-3)."""

    memo: str  # the final assistant content (Markdown)
    steps: int  # LLM calls spent in the loop (a step == one LLM call)
    step_limit_hit: bool  # True when the forced-answer path fired


def run_research(db: Session, session_id: str, query: str) -> ResearchResult:
    """Run the evidence loop for one research query and return the memo.

    Three exits: the model answers without tool calls (its content is the memo);
    the step budget runs out (one final call without tools forces a best-effort
    answer, marked with an explicit step-limit note); or the gateway raises
    AppError, which propagates to the caller like any other LLM failure.
    Every gateway call is logged with route='agent' and its 1-based step index.
    """
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"Date: {date.today()}. User's question: {query}",
        },
    ]

    tools = [spec.schema for spec in TOOLS.values()]

    for step in range(1, MAX_STEPS):
        msg = llm_client.chat_message(
            messages=messages,
            tools=tools,
            db=db,
            session_id=session_id,
            route="agent",
            step=step,
        )

        messages.append(msg)

        if not msg.tool_calls:
            return ResearchResult(memo=msg.content, steps=step, step_limit_hit=False)

        for tool_call in msg.tool_calls:
            result = _execute_tool_call(db, session_id, tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    messages.append(
        {
            "role": "user",
            "content": (
                "You have reached the step limit. Answer now with what you have. "
                "Keep the [chunk:<id>] tags on claims supported by search_documents "
                "passages; mark unsupported key claims [unverified]."
            ),
        }
    )
    step += 1
    final = llm_client.chat_message(
        messages=messages,
        db=db,
        session_id=session_id,
        route="agent",
        step=step,
    )
    return ResearchResult(
        memo=final.content + "\n\n_Note: step limit reached._",
        steps=step,
        step_limit_hit=True,
    )


def _execute_tool_call(db: Session, session_id: str, tool_call: object) -> str:
    """Execute one tool call and return the tool-result text. Never raises.

    Errors are data: malformed model-generated arguments, hallucinated tool
    names, service AppErrors, and unexpected exceptions all come back as
    "Error: ..." strings — specific text is what lets the model route around
    a failure and keeps the loop alive.
    """
    name = tool_call.function.name
    if name not in TOOLS:
        return f"Error: unknown tool name. Valid tools: {', '.join(TOOLS)}"

    try:
        args = json.loads(tool_call.function.arguments)
        spec = TOOLS[name]
        return spec.fn(db, session_id, **args)
    except json.JSONDecodeError as e:
        return f"Error: {name} malformed arguments: {tool_call.function.arguments} has {e}"
    except AppError as e:
        return "Error: " + e.message
    except Exception as e:
        return f"Error: tool failed: {e}"
