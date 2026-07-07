"""The Research Agent's hand-written tool-use loop (ReAct-shaped). Core module — owner-written.

Drives the tool-calling conversation shape:

    system -> user -> assistant(tool_calls) -> tool results (one per id) -> ... -> assistant(content)

Design decisions D1-D7 are in the Phase 13 design lesson; each TODO below marks
one of them. Binding constraints: every LLM call goes through the llm_client
gateway (never instantiate a client here); messages are append-only (prefix
caching depends on it); errors inside tools are fed back as tool results, never
raised out of the loop (D5); the step budget is the loop's own safety rail (D2).
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.modules.ai.agent.tools import TOOLS  # noqa: F401 — used by the owner's implementation

from app.core.errors import AppError

import json

MAX_STEPS = 8

# TODO(owner, prefix placement): write the static system prompt as a frozen
# module-level constant. Requirements:
#   - byte-stable across runs: no dates, no query text, no session data
#     (per-run data belongs in the *user* message, appended at call time)
#   - research-agent persona: gather evidence with the provided read-only tools
#     before answering; never fabricate numbers; produce an evidence memo
#     (findings + sources), NOT trade instructions
#   - the financial-advice safety boundary verbatim — see the block in
#     prompt_builder.py lines 25-30 (flag in review if you want it extracted
#     into a shared constant instead of duplicated)
SYSTEM_PROMPT = "TODO"


@dataclass(frozen=True)
class ResearchResult:
    """What a research run produces (consumed by report_generator in PR-3)."""

    memo: str  # the final assistant content (Markdown)
    steps: int  # LLM calls spent in the loop (D2: a step == one LLM call)
    step_limit_hit: bool  # True when the D3 forced-answer path fired


def run_research(db: Session, session_id: str, query: str) -> ResearchResult:
    """Run the evidence loop for one research query and return the memo.

    TODO(owner): implement per the design lesson.
      D1 - three exits only: natural answer (assistant message without tool
           calls -> its content is the memo), step budget exhausted (-> D3),
           gateway AppError propagates (do NOT catch it here).
      D2 - count steps in LLM calls made by this loop; enforce MAX_STEPS.
      D3 - the forced final call omits the tools parameter (mechanism, not
           instruction) + appends a brief "answer now with what you have"
           user/system nudge; set step_limit_hit and add an explicit
           "step limit reached" note to the memo.
      D4 - execute a multi-call batch sequentially; append the assistant
           message FIRST, then exactly one tool message per tool_call_id.
      D7 - pass route='agent' and step=<1-based index> into the gateway on
           every call so llm_calls rows attribute the run correctly.
    """
    raise NotImplementedError  # TODO(owner)


def _execute_tool_call(db: Session, session_id: str, tool_call: object) -> str:
    """Execute one tool call and return the tool-result text. Never raises (D5).

    TODO(owner): errors are data —
      - arguments are model-generated JSON text: json.loads may fail
        -> return "Error: malformed arguments ..." naming the problem
      - unknown tool name (model hallucination) -> "Error: unknown tool ...,
        valid tools: ..." so the model can steer
      - AppError from a service (e.g. unknown ticker) -> its message as
        "Error: ..." (specific text is what lets the model route around)
      - any other Exception -> generic "Error: tool failed: ..."
      - success -> the tool's compact string output, unchanged
    Bind db + session_id; look up the callable in TOOLS.
    """
    name = tool_call.function.name
    if name not in TOOLS:
        return f"Error: unknown tool name. Valid tools: {', '.join(TOOLS)}"

    try:
        args = json.loads(tool_call.function.arguments)

        spec = TOOLS[name]
        return spec.fn(db, session_id, **args)

    except json.JSONDecodeError as e:
        return f"Error: {name} malform arguments: {tool_call.function.arguments} has {e}"
    except AppError as e:
        return "Error: " + e.message
    except Exception as e:
        return f"Error: tool failed: {e}"
