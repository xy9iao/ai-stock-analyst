"""fts gin index on document_chunks

Revision ID: 80ad439a5932
Revises: c953934595fd
Create Date: 2026-07-20 17:22:56.871397
"""

from collections.abc import Sequence

from alembic import op

revision: str = '80ad439a5932'
down_revision: str | None = 'c953934595fd'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Expression index matching the lexical-pool query in ai/rag/retrieval.py:
    # WHERE to_tsvector('english', content) @@ websearch_to_tsquery(...).
    # The expression must match the query verbatim for the planner to use it.
    op.execute(
        "CREATE INDEX ix_document_chunks_content_fts "
        "ON document_chunks USING GIN (to_tsvector('english', content))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX ix_document_chunks_content_fts")
