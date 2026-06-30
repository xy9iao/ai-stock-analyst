"""The single OpenAI-compatible LLM call site. Every LLM request goes through here.

Centralizes the client, the model/endpoint config, and error handling, so prompt
construction and the financial-advice boundary live in one place (prompt_builder).
"""

from openai import OpenAI

from app.core.config import settings
from app.core.errors import AppError


def _client() -> OpenAI:
    return OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


def chat(messages: list[dict[str, str]], *, temperature: float = 0.6) -> str:
    """Run a multi-turn chat completion and return the assistant's text.

    `messages` is the full list (system + prior turns + new user message).
    Missing key -> AppError(503); any LLM/network failure -> AppError(502).
    """
    if not settings.llm_api_key:
        raise AppError(
            code="llm_not_configured",
            message="LLM_API_KEY is not set",
            status_code=503,
        )
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

    return response.choices[0].message.content or ""


def complete(system: str, user: str, *, temperature: float = 0.4) -> str:
    """Single-turn convenience wrapper over chat()."""
    return chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
