"""Tests for the embeddings gateway (rag/embeddings_client). Provider faked."""

from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.core.errors import AppError
from app.modules.ai.rag import embeddings_client


def _response(vectors: list[list[float]], prompt_tokens: int = 7):
    return SimpleNamespace(
        data=[SimpleNamespace(embedding=v) for v in vectors],
        usage=SimpleNamespace(prompt_tokens=prompt_tokens),
    )


def _install(monkeypatch: pytest.MonkeyPatch, response) -> SimpleNamespace:
    def _create(**kwargs):
        fake.kwargs = kwargs
        if isinstance(response, Exception):
            raise response
        return response

    fake = SimpleNamespace(embeddings=SimpleNamespace(create=_create), kwargs=None)
    monkeypatch.setattr(embeddings_client, "_client", lambda: fake)
    monkeypatch.setattr(settings, "embedding_api_key", "test-key")
    return fake


def test_embeds_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _install(monkeypatch, _response([[0.1, 0.2], [0.3, 0.4]]))
    vectors = embeddings_client.embed_texts(["a", "b"])
    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert fake.kwargs["input"] == ["a", "b"]
    assert fake.kwargs["model"] == settings.embedding_model


def test_empty_input_no_call(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _install(monkeypatch, _response([]))
    assert embeddings_client.embed_texts([]) == []
    assert fake.kwargs is None  # provider never called


def test_missing_key_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "embedding_api_key", "")
    with pytest.raises(AppError) as err:
        embeddings_client.embed_texts(["a"])
    assert err.value.status_code == 503


def test_provider_error_wrapped_502(monkeypatch: pytest.MonkeyPatch) -> None:
    _install(monkeypatch, RuntimeError("boom"))
    with pytest.raises(AppError) as err:
        embeddings_client.embed_texts(["a"])
    assert err.value.status_code == 502
