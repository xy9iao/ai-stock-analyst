from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.database import Base
from app.models.base import TimestampMixin


class DocumentChunk(TimestampMixin, Base):
    """One retrievable chunk of an ingested document (Phase 14 RAG).

    Not session-scoped: the corpus is shared read-only reference data, like
    market_data_cache. The embedding dimension is frozen at table-creation
    time — switching embedding models requires re-embedding and a migration.
    """

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.embedding_dimensions), nullable=False
    )
