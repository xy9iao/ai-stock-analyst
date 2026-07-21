"""Database access for chat sessions and messages.

`demo_session_id` is the anonymous demo bucket (cookie); `session_id: int` is a
chat conversation's primary key. Distinct concepts — keep the names apart.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession


def create_session(db: Session, title: str | None, demo_session_id: str) -> ChatSession:
    session = ChatSession(title=title, session_id=demo_session_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: int, demo_session_id: str) -> ChatSession | None:
    session = db.get(ChatSession, session_id)
    if session is not None and session.session_id != demo_session_id:
        return None
    return session


def set_summary(db: Session, session: ChatSession, summary: str) -> None:
    """Persist the running compression summary (Phase 15) on its session row."""
    session.summary = summary
    db.commit()


def list_sessions(db: Session, demo_session_id: str, limit: int = 50) -> list[ChatSession]:
    rows = db.scalars(
        select(ChatSession)
        .where(ChatSession.session_id == demo_session_id)
        .order_by(ChatSession.created_at.desc())
        .limit(limit)
    ).all()
    return list(rows)


def count_llm_replies(db: Session, demo_session_id: str) -> int:
    """Assistant messages across all of this demo session's conversations —
    the unit for the chat cost cap (LLM calls, not HTTP requests)."""
    rows = db.scalars(
        select(ChatMessage.id)
        .join(ChatSession, ChatMessage.chat_session_id == ChatSession.id)
        .where(ChatSession.session_id == demo_session_id, ChatMessage.role == "assistant")
    ).all()
    return len(rows)


def add_message(db: Session, session_id: int, role: str, content: str) -> ChatMessage:
    message = ChatMessage(chat_session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, session_id: int) -> list[ChatMessage]:
    rows = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == session_id)
        .order_by(ChatMessage.created_at)
    ).all()
    return list(rows)
