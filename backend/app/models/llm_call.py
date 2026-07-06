from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import SessionScopedMixin, TimestampMixin


class LlmCall(SessionScopedMixin, TimestampMixin, Base):
    """One row per LLM call — token/latency observability, written by llm_client.

    `route` and `steps` stay NULL in v0; they are pre-seeded for the agent
    version (pipeline-vs-agent routing and loop step counts) so the log schema
    won't need to change.
    """

    __tablename__ = "llm_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(40), index=True, nullable=False)  # report | chat
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    cached_tokens: Mapped[int | None] = mapped_column(Integer)  # provider cache hits (Phase 13)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    route: Mapped[str | None] = mapped_column(String(40))
    steps: Mapped[int | None] = mapped_column(Integer)
