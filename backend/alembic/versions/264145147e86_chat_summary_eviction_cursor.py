"""chat summary eviction cursor

Revision ID: 264145147e86
Revises: 8b3d21a7ca92
Create Date: 2026-07-21 16:00:30.006370
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = '264145147e86'
down_revision: str | None = '8b3d21a7ca92'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Hand-adjusted: removed autogenerate's spurious drop of the FTS expression
    # index (invisible to model metadata — see 8b3d21a7ca92 for the same fix).
    op.add_column('chat_sessions', sa.Column('summarized_through_message_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('chat_sessions', 'summarized_through_message_id')
