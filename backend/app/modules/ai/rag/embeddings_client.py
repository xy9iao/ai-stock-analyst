"""The single embedding call site (Phase 14), sibling of llm_client.

Embeddings use a separate provider from the LLM (DeepSeek has no embeddings
API), configured by EMBEDDING_API_KEY / EMBEDDING_MODEL. Every batch call is
recorded in llm_calls (kind='embed') so cost attribution stays complete.
"""

import time

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.modules.ai.llm_client import _record_call

_MAX_BATCH = 256  # OpenAI hard limit is 2048 inputs; keep batches comfortably small


def _client() -> OpenAI:
    return OpenAI(api_key=settings.embedding_api_key)


def embed_texts(texts: list[str], *, db: Session | None = None) -> list[list[float]]:
    """Embed a batch of texts, preserving order. Raises AppError(503/502)."""
    if not texts:
        return []
    if not settings.embedding_api_key:
        raise AppError(
            code="embeddings_not_configured",
            message="EMBEDDING_API_KEY is not set",
            status_code=503,
        )

    vectors: list[list[float]] = []
    for start in range(0, len(texts), _MAX_BATCH):
        batch = texts[start : start + _MAX_BATCH]
        started = time.monotonic()
        try:
            response = _client().embeddings.create(model=settings.embedding_model, input=batch)
        except Exception as exc:
            raise AppError(
                code="embeddings_error",
                message=f"Embedding request failed: {exc}",
                status_code=502,
            ) from exc
        latency_ms = int((time.monotonic() - started) * 1000)

        vectors.extend(item.embedding for item in response.data)
        if db is not None:
            usage = getattr(response, "usage", None)
            _record_call(
                db,
                session_id="local",
                kind="embed",
                latency_ms=latency_ms,
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=None,
                model=settings.embedding_model,
            )
    return vectors
