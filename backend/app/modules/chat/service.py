"""Chat orchestration: history + toggled context -> LLM -> persist -> reply."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.modules.ai import llm_client
from app.modules.chat import compression
from app.modules.chat import context as chat_context
from app.modules.chat import repository
from app.modules.chat.schemas import ChatMessageRequest

_SYSTEM_PROMPT = """You are an investment research assistant for a beginner investor, \
focused on stocks, investing, market news, and portfolio questions. You are NOT a \
licensed financial advisor and do not give guaranteed financial advice.

- Stay on investment-related topics. If asked something unrelated, briefly redirect the \
user back to investing.
- Use the provided context (holdings, watchlist, a focus stock, recent reports) when \
relevant; if context is missing, answer from general knowledge and say so.
- Be clear and beginner-friendly. Avoid "guaranteed", "risk-free", "you must buy"; prefer \
"based on available data", "consider", "the risk is"."""

_HISTORY_LIMIT = 20


def _enforce_demo_cap(db: Session, demo_session_id: str) -> None:
    """Cost-defense layer 3: per-session cap counted in LLM calls, not requests."""
    if not settings.demo_mode:
        return
    if repository.count_llm_replies(db, demo_session_id) >= settings.demo_chat_llm_limit:
        raise AppError(
            code="demo_chat_limit",
            message=(
                f"Demo limit reached: max {settings.demo_chat_llm_limit} chat replies per "
                "session. Start a new demo session to continue."
            ),
            status_code=429,
        )


def send_message(db: Session, request: ChatMessageRequest, demo_session_id: str) -> tuple[int, str]:
    _enforce_demo_cap(db, demo_session_id)

    if request.session_id is not None:
        session = repository.get_session(db, request.session_id, demo_session_id)
        if session is None:
            raise AppError(
                code="chat_session_not_found",
                message=f"Chat session {request.session_id} not found",
                status_code=404,
            )
    else:
        session = repository.create_session(db, request.message[:60], demo_session_id)

    # Ordering (Phase 15, cache-preserving): static system -> (optional) context ->
    # running summary -> verbatim history -> the new user message.
    messages: list[dict[str, str]] = [{"role": "system", "content": _SYSTEM_PROMPT}]
    context_block = chat_context.build_context(db, request.context, demo_session_id)
    if context_block:
        messages.append({"role": "system", "content": "Context:\n" + context_block})

    rows = repository.list_messages_after(db, session.id, session.summarized_through_message_id)
    history = [{"role": past.role, "content": past.content} for past in rows]
    summary = session.summary
    if compression.needs_compression(history):
        try:
            summary, history = compression.compress(db, demo_session_id, summary, history)
            evicted_count = len(rows) - len(history)
            if evicted_count > 0:  # compress no-ops when history fits the window
                repository.set_summary(db, session, summary, rows[evicted_count - 1].id)
        except AppError:
            # Compression is an optimization: degrade to the v0 cap, never block chat.
            history = history[-_HISTORY_LIMIT:]
    if summary:
        messages.append({"role": "system", "content": "Conversation so far (summary):\n" + summary})
    messages.extend(history)
    messages.append({"role": "user", "content": request.message})

    reply = llm_client.chat(messages, db=db, session_id=demo_session_id, kind="chat")

    # Persist both turns only after a successful reply.
    repository.add_message(db, session.id, "user", request.message)
    repository.add_message(db, session.id, "assistant", reply)
    return session.id, reply
