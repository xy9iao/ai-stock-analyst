"""Database access for chat sessions and messages."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ChatMessage, ChatSession


def create_session(db: Session, title: str | None = None) -> ChatSession:
    session = ChatSession(title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: int) -> ChatSession | None:
    return db.get(ChatSession, session_id)


def list_sessions(db: Session, limit: int = 50) -> list[ChatSession]:
    rows = db.scalars(
        select(ChatSession).order_by(ChatSession.created_at.desc()).limit(limit)
    ).all()
    return list(rows)


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
