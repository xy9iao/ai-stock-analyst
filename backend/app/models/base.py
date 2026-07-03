from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class SessionScopedMixin:
    """Buckets a row under an anonymous demo session (see core/demo_session.py).

    Locally everything uses the permanent "local" bucket — the server_default
    also backfills pre-demo rows in the migration.
    """

    session_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, server_default="local"
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
