"""Ingestion pipeline: news URLs -> article bodies -> chunks -> embeddings -> DB.

Per-document failures (unreachable URL, paywall, empty extraction) are logged
and skipped — one dead link never sinks an ingest run. Re-ingesting a URL
replaces its chunks (delete-then-insert), so runs are idempotent and chunk
indexes stay stable per (source_url, chunk_index).
"""

import logging
from dataclasses import dataclass

import trafilatura
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.modules.ai.rag.chunking import chunk_text
from app.modules.ai.rag.embeddings_client import embed_texts
from app.modules.news import service as news_service

logger = logging.getLogger(__name__)

_MAX_DOCS_PER_RUN = 10


@dataclass(frozen=True)
class IngestStats:
    ticker: str
    docs_ingested: int
    docs_skipped: int
    chunks_written: int


def _fetch_body(url: str) -> str | None:
    """Download and extract the readable article text; None on any failure."""
    try:
        html = trafilatura.fetch_url(url)
        if not html:
            return None
        return trafilatura.extract(html)
    except Exception:
        logger.warning("ingest: fetch/extract failed for %s", url, exc_info=True)
        return None


def ingest_ticker(db: Session, ticker: str, *, max_docs: int = _MAX_DOCS_PER_RUN) -> IngestStats:
    """Ingest the current news set for a ticker into document_chunks."""
    symbol = ticker.strip().upper()
    news = news_service.get_company_news(db, symbol)

    ingested = skipped = written = 0
    for item in news.items[:max_docs]:
        if not item.url:
            skipped += 1
            continue
        body = _fetch_body(item.url)
        if not body:
            skipped += 1
            continue

        chunks = chunk_text(body)
        if not chunks:
            skipped += 1
            continue
        vectors = embed_texts(chunks, db=db)

        # Idempotent re-ingest: replace this URL's chunks wholesale.
        db.execute(delete(DocumentChunk).where(DocumentChunk.source_url == item.url))
        for index, (content, vector) in enumerate(zip(chunks, vectors)):
            db.add(
                DocumentChunk(
                    source_url=item.url,
                    title=item.headline[:512],
                    ticker=symbol,
                    published_at=item.published_at,
                    chunk_index=index,
                    content=content,
                    embedding=vector,
                )
            )
        ingested += 1
        written += len(chunks)

    db.commit()
    logger.info(
        "ingest: ticker=%s docs=%d skipped=%d chunks=%d", symbol, ingested, skipped, written
    )
    return IngestStats(
        ticker=symbol, docs_ingested=ingested, docs_skipped=skipped, chunks_written=written
    )
