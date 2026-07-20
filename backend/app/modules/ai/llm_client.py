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
from openai.types.chat import ChatCompletionMessage
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
    cached_tokens: int | None = None,
    route: str | None = None,
    steps: int | None = None,
    model: str | None = None,
) -> None:
    """Best-effort observability — a logging failure must never break the reply.

    `model` defaults to the chat LLM; the embeddings client passes its own.
    """
    from app.models import LlmCall  # local import to keep module import cheap

    model = model or settings.llm_model
    logger.info(
        "llm_call kind=%s model=%s latency_ms=%d prompt_tokens=%s completion_tokens=%s",
        kind,
        model,
        latency_ms,
        prompt_tokens,
        completion_tokens,
    )
    try:
        db.add(
            LlmCall(
                session_id=session_id,
                kind=kind,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cached_tokens=cached_tokens,
                latency_ms=latency_ms,
                route=route,
                steps=steps,
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
    msg = chat_message(
        messages,
        temperature=temperature,
        db=db,
        session_id=session_id,
        kind=kind,
    )
    return msg.content or ""


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
) -> ChatCompletionMessage:
    """Run a completion and return the full assistant message.

    The gateway's execution core: chat()/complete() delegate here, and the
    agent loop calls it directly to read `.tool_calls` off the result.
    `tools` (OpenAI function schemas) is forwarded to the provider only when
    provided; `route`/`step` are recorded on the llm_calls row.

    Missing key -> AppError(503); demo switch off -> AppError(503);
    any LLM/network failure -> AppError(502).
    """
    if not settings.llm_api_key:
        raise AppError(
            code="llm_not_configured",
            message="LLM_API_KEY is not set",
            status_code=503,
        )

    if settings.demo_mode and db is not None and not llm_switch.is_enabled(db):
        raise AppError(
            code="llm_disabled",
            message="The demo LLM is currently switched off. Please try again later.",
            status_code=503,
        )

    kwargs: dict = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": temperature,
    }
    if tools:
        kwargs["tools"] = tools

    started = time.monotonic()
    try:
        response = _client().chat.completions.create(**kwargs)
    except Exception as exc:  # openai raises varied errors (auth, rate limit, network)
        raise AppError(
            code="llm_error",
            message=f"LLM request failed: {exc}",
            status_code=502,
        ) from exc
    latency_ms = int((time.monotonic() - started) * 1000)

    usage = getattr(response, "usage", None)

    # Cache-hit count: OpenAI reports usage.prompt_tokens_details.cached_tokens;
    # DeepSeek reports usage.prompt_cache_hit_tokens. Either level may be absent
    # or None depending on the provider, hence the guarded hops.
    details = getattr(usage, "prompt_tokens_details", None)
    cached_tokens = getattr(details, "cached_tokens", None)
    if cached_tokens is None:
        cached_tokens = getattr(usage, "prompt_cache_hit_tokens", None)

    if db is not None:
        _record_call(
            db,
            session_id=session_id,
            kind=kind,
            latency_ms=latency_ms,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            cached_tokens=cached_tokens,
            route=route,
            steps=step,
        )

    return response.choices[0].message


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
