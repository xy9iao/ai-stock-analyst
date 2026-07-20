"""Corpus inspector: what's ingested right now (for authoring citation atoms).

Usage, from backend/:  uv run python -m eval.corpus [grep-term]
"""

import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import DocumentChunk


def main() -> int:
    needle = sys.argv[1].lower() if len(sys.argv) > 1 else None
    db = SessionLocal()
    try:
        rows = db.scalars(select(DocumentChunk).order_by(DocumentChunk.id)).all()
        seen_urls: set[str] = set()
        for row in rows:
            if needle and needle not in row.content.lower():
                continue
            if needle:
                pos = row.content.lower().find(needle)
                snippet = row.content[max(0, pos - 60) : pos + 100].replace("\n", " ")
                print(f"chunk {row.id} [{row.ticker}] {row.title[:60]!r}: …{snippet}…")
            elif row.source_url not in seen_urls:
                seen_urls.add(row.source_url)
                date = str(row.published_at)[:10] if row.published_at else "n.d."
                print(f"[{row.ticker}] {date} {row.title[:80]}")
        if not needle:
            print(f"\n{len(rows)} chunks across {len(seen_urls)} documents")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
