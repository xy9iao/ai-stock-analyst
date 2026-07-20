"""Hybrid retrieval (Phase 14): pgvector cosine + FTS→BM25, fused with RRF.

The single retrieval path — the pipeline's fixed step and the agent's
search_documents tool both call hybrid_search. Parameters are regression-gated.
"""

import logging

from rank_bm25 import BM25Okapi
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import DocumentChunk
from app.modules.ai.rag.embeddings_client import embed_texts

logger = logging.getLogger(__name__)

POOL_SIZE = 50  # per-path candidate pool: FTS/vector recall is the only job here
TOP_K = 8  # final chunks -> ~3.6k tokens of retrieved context at 1800-char chunks
RRF_K = 60  # rank damper from the RRF paper; ranks 1 vs 2 differ by ~0.03% of scale


def rrf_fuse(rankings: list[list[int]], k: int = RRF_K) -> list[int]:
    """Fuse ranked id lists: score(id) = Σ 1/(k + rank), best first.

    Rank-based on purpose: cosine and BM25 scores live in different universes,
    and rank is the only scale-free common currency. Ties break on id so the
    output is deterministic (the regression set requires it).
    """
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))


def bm25_rescore(query: str, candidates: list[DocumentChunk]) -> list[DocumentChunk]:
    """Reorder FTS candidates by BM25 computed over the pool.

    IDF is pool-relative, not corpus-relative — the accepted skew of doing
    BM25 in the app layer (Neon has no pg_search). Zero-overlap queries leave
    all scores at 0, and the stable sort preserves FTS order as the fallback.
    """
    if not candidates:
        return []
    tokenized = [c.content.lower().split() for c in candidates]
    scores = BM25Okapi(tokenized).get_scores(query.lower().split())
    order = sorted(range(len(candidates)), key=lambda i: (-scores[i], i))
    return [candidates[i] for i in order]


def _vector_pool(db: Session, query: str, ticker: str | None) -> list[DocumentChunk]:
    vector = embed_texts([query], db=db)[0]
    stmt = select(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(vector))
    if ticker:
        stmt = stmt.where(DocumentChunk.ticker == ticker.strip().upper())
    return list(db.scalars(stmt.limit(POOL_SIZE)))


def _lexical_pool(db: Session, query: str, ticker: str | None) -> list[DocumentChunk]:
    tsvector = func.to_tsvector("english", DocumentChunk.content)
    tsquery = func.websearch_to_tsquery("english", query)
    stmt = (
        select(DocumentChunk)
        .where(tsvector.op("@@")(tsquery))
        .order_by(func.ts_rank(tsvector, tsquery).desc())
    )
    if ticker:
        stmt = stmt.where(DocumentChunk.ticker == ticker.strip().upper())
    return list(db.scalars(stmt.limit(POOL_SIZE)))


def hybrid_search(
    db: Session, query: str, *, ticker: str | None = None, top_k: int = TOP_K
) -> list[DocumentChunk]:
    """The one retrieval entry point. Never raises on path failure:
    if the vector path is down (embeddings 5xx), lexical results still flow —
    degraded retrieval must never take a report down.
    """
    try:
        vector_pool = _vector_pool(db, query, ticker)
    except AppError:
        logger.warning("hybrid_search: vector path unavailable, lexical only")
        vector_pool = []
    lexical_pool = bm25_rescore(query, _lexical_pool(db, query, ticker))

    fused = rrf_fuse([[c.id for c in vector_pool], [c.id for c in lexical_pool]])
    by_id = {c.id: c for c in vector_pool + lexical_pool}
    return [by_id[chunk_id] for chunk_id in fused[:top_k]]
