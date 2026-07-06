"""The single OpenAI-compatible LLM call site. Every LLM request goes through here.

Centralizes the client, the model/endpoint config, and error handling, so prompt
construction and the financial-advice boundary live in one place (prompt_builder).
Being the single gateway also makes it the one place for:
- the demo **master switch** check (cost-defense layer 2, core/llm_switch.py)
- per-call **observability** (tokens/latency into the llm_calls table + a log line)
"""

import logging
import time

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core import llm_switch
from app.core.config import settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)


def _client() -> OpenAI:
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        timeout=settings.llm_timeout_seconds,
    )


def _record_call(
    db: Session,
    *,
    session_id: str,
    kind: str,
    latency_ms: int,
    prompt_tokens: int | None,
    completion_tokens: int | None,
) -> None:
    """Best-effort observability — a logging failure must never break the reply."""
    from app.models import LlmCall  # local import to keep module import cheap

    logger.info(
        "llm_call kind=%s model=%s latency_ms=%d prompt_tokens=%s completion_tokens=%s",
        kind,
        settings.llm_model,
        latency_ms,
        prompt_tokens,
        completion_tokens,
    )
    try:
        db.add(
            LlmCall(
                session_id=session_id,
                kind=kind,
                model=settings.llm_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("failed to record llm_call row")


def chat(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.6,
    db: Session | None = None,
    session_id: str = "local",
    kind: str = "chat",
) -> str:
    """Run a multi-turn chat completion and return the assistant's text.

    `messages` is the full list (system + prior turns + new user message).
    Missing key -> AppError(503); demo switch off -> AppError(503);
    any LLM/network failure -> AppError(502).
    """
    if not settings.llm_api_key:
        raise AppError(
            code="llm_not_configured",
            message="LLM_API_KEY is not set",
            status_code=503,
        )
    # Cost-defense layer 2: in demo mode the LLM is OFF unless the admin
    # switch was turned on (and its TTL hasn't expired).
    if settings.demo_mode and db is not None and not llm_switch.is_enabled(db):
        raise AppError(
            code="llm_disabled",
            message="The demo LLM is currently switched off. Please try again later.",
            status_code=503,
        )

    started = time.monotonic()
    try:
        response = _client().chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=temperature,
        )
    except Exception as exc:  # openai raises varied errors (auth, rate limit, network)
        raise AppError(
            code="llm_error",
            message=f"LLM request failed: {exc}",
            status_code=502,
        ) from exc
    latency_ms = int((time.monotonic() - started) * 1000)

    usage = getattr(response, "usage", None)
    if db is not None:
        _record_call(
            db,
            session_id=session_id,
            kind=kind,
            latency_ms=latency_ms,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )

    return response.choices[0].message.content or ""


def chat_message(
    messages: list[dict],
    *,
    tools: list[dict] | None = None,
    temperature: float = 0.6,
    db: Session | None = None,
    session_id: str = "local",
    kind: str = "research",
    route: str | None = None,
    step: int | None = None,
):
    """Gateway entry for tool-calling turns: returns the FULL assistant message
    (so callers can read `.tool_calls`), unlike chat() which returns text.

    TODO(owner, gateway seam): implement per the design lesson (§3, shape (a)):
      - share ONE execution core with chat(): api-key check + demo master-switch
        check + timeout + AppError wrapping must run for every call — refactor
        the shared part out of chat() rather than duplicating it
      - pass `tools=tools` to the OpenAI call only when provided
      - record the llm_calls row for every call, now including:
          cached_tokens  <- usage.prompt_tokens_details.cached_tokens,
                            falling back to usage.prompt_cache_hit_tokens
                            (spike: both fields exist, same number)
          route, steps   <- the new route/step arguments (D7)
        which means extending _record_call's signature — keep it best-effort
        (a logging failure must never break the reply)
      - return response.choices[0].message unchanged
      - then make chat() delegate to the same core so there is still exactly
        one code path that talks to the provider
    """
    raise NotImplementedError  # TODO(owner)


def complete(
    system: str,
    user: str,
    *,
    temperature: float = 0.4,
    db: Session | None = None,
    session_id: str = "local",
    kind: str = "report",
) -> str:
    """Single-turn convenience wrapper over chat()."""
    return chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        db=db,
        session_id=session_id,
        kind=kind,
    )
