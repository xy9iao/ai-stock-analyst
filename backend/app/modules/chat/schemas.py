"""Request/response schemas for the chat module."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatContextOptions(BaseModel):
    """Toggles for which DB context the assistant should inject (the future UI's buttons)."""

    include_holdings: bool = False
    include_watchlist: bool = False
    ticker: str | None = None
    include_recent_reports: bool = False


class ChatMessageRequest(BaseModel):
    """POST body. Omit session_id to start a new conversation."""

    message: str = Field(min_length=1)
    session_id: int | None = None
    context: ChatContextOptions = Field(default_factory=ChatContextOptions)


class ChatReply(BaseModel):
    """Response to a posted message."""

    session_id: int
    reply: str


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    created_at: datetime
