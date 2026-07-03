"""HTTP routes for chat."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.demo_session import get_session_id
from app.core.errors import AppError
from app.modules.chat import repository, service
from app.modules.chat.schemas import (
    ChatMessageRead,
    ChatMessageRequest,
    ChatReply,
    ChatSessionRead,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/messages", status_code=status.HTTP_201_CREATED)
def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    demo_session_id: str = Depends(get_session_id),
) -> ChatReply:
    session_id, reply = service.send_message(db, request, demo_session_id)
    return ChatReply(session_id=session_id, reply=reply)


@router.get("/sessions")
def list_sessions(
    db: Session = Depends(get_db), demo_session_id: str = Depends(get_session_id)
) -> list[ChatSessionRead]:
    return repository.list_sessions(db, demo_session_id)


@router.get("/sessions/{session_id}/messages")
def list_messages(
    session_id: int,
    db: Session = Depends(get_db),
    demo_session_id: str = Depends(get_session_id),
) -> list[ChatMessageRead]:
    if repository.get_session(db, session_id, demo_session_id) is None:
        raise AppError(
            code="chat_session_not_found",
            message=f"Chat session {session_id} not found",
            status_code=404,
        )
    return repository.list_messages(db, session_id)
