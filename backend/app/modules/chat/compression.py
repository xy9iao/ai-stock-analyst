"""Chat history compression (Phase 15): batch eviction into a running summary.

The prompt stays append-only between compression events (prefix-cache friendly);
an event folds all-but-the-last-N messages into one flash-tier summary call.
The DB keeps every message regardless — compression decides what the PROMPT
sees, never what is stored.
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.ai import llm_client

SUMMARY_PROMPT = """You maintain the running summary of an investment chat's older turns. \
Merge the previous summary (if any) with the newly provided turns into ONE updated summary.

Preserve exactly, never paraphrase away:
- tickers and all numbers (prices, quantities, percentages) as stated
- every prior recommendation with its action label and confidence
- the user's stated holdings, constraints, and risk tolerance
- unresolved questions

Rules: never add facts, advice, or speculation that is not in the input; \
drop pleasantries and repetition; write compact prose, at most ~200 words."""


def estimate_tokens(messages: list[dict]) -> int:
    """~4 chars/token heuristic — same dependency-free choice as the chunker."""
    return sum(len(m["content"]) for m in messages) // 4


def needs_compression(messages: list[dict]) -> bool:
    return estimate_tokens(messages) > settings.chat_compress_threshold_tokens


def compress(
    db: Session | None,
    demo_session_id: str,
    prior_summary: str | None,
    messages: list[dict],
) -> tuple[str, list[dict]]:
    """Fold all-but-the-last-N messages into the running summary.

    Returns (new_summary, verbatim_window). Raises AppError on LLM failure —
    the caller owns the fallback (degrade to capped history, never block chat).
    """
    keep = settings.chat_verbatim_messages
    if len(messages) <= keep:
        return (prior_summary or "", messages)

    evicted, kept = messages[:-keep], messages[-keep:]
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in evicted)
    payload = (
        f"Previous summary:\n{prior_summary}\n\n" if prior_summary else ""
    ) + f"Turns to fold in:\n{transcript}"
    new_summary = llm_client.complete(
        SUMMARY_PROMPT,
        payload,
        temperature=0.2,
        db=db,
        session_id=demo_session_id,
        kind="summarize",
    )
    return new_summary, kept
