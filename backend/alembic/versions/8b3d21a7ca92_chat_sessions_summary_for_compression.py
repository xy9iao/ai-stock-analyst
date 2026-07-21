"""chat_sessions summary for compression

Revision ID: 8b3d21a7ca92
Revises: 80ad439a5932
Create Date: 2026-07-21 14:53:26.711045
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '8b3d21a7ca92'
down_revision: str | None = '80ad439a5932'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Hand-adjusted: autogenerate wanted to drop ix_document_chunks_content_fts —
    # expression indexes are invisible to model metadata and get flagged as strays.
    # Never accept that drop; the index is created by 80ad439a5932.
    op.add_column('chat_sessions', sa.Column('summary', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('chat_sessions', 'summary')
