"""Save-time citation rendering: [chunk:N] tags -> numbered source links.

The rewrite happens in the stored Markdown itself (not the frontend) so
citations survive the standalone-Markdown export. Validation is deterministic
set-membership — no model judges a model. A hallucinated tag is stripped and
the degradation is visibly noted; the report never fails over citations.
"""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk

_TAG = re.compile(r" ?\[chunk:(\d+)\]")
_UNVERIFIED_BADGE = "**[⚠ unverified]**"
_DEGRADE_NOTE = "\n\n_Note: some citations could not be verified and were removed._"
_SOURCE_PREVIEW_CHARS = 600


def format_sources(chunks: list[DocumentChunk]) -> str:
    """The Sources block injected into prompts — same [chunk:id] shape the
    search_documents tool emits, so both paths teach the model one format."""
    lines = ["Sources (cite key claims with the matching [chunk:id] tag):"]
    for chunk in chunks:
        date = str(chunk.published_at)[:10] if chunk.published_at else "n.d."
        lines.append(
            f"[chunk:{chunk.id}] {chunk.title} ({date}) {chunk.source_url}\n"
            f"{chunk.content[:_SOURCE_PREVIEW_CHARS]}"
        )
    return "\n\n".join(lines)


def cited_ids(markdown: str) -> list[int]:
    """Distinct cited chunk ids, in order of first appearance."""
    seen: list[int] = []
    for match in _TAG.finditer(markdown):
        chunk_id = int(match.group(1))
        if chunk_id not in seen:
            seen.append(chunk_id)
    return seen


def invalid_ids(db: Session, markdown: str, allowed: set[int] | None = None) -> set[int]:
    """Cited ids that cannot be linked.

    `allowed` = the retrieved set (pipeline path, strict membership check);
    None = any chunk that exists in the DB passes (agent path — the loop does
    not track which chunks its tool calls returned; existence is the weaker
    but honest check, recorded as a known limit).
    """
    ids = set(cited_ids(markdown))
    if not ids:
        return set()
    if allowed is not None:
        return ids - allowed
    existing = set(db.scalars(select(DocumentChunk.id).where(DocumentChunk.id.in_(ids))))
    return ids - existing


def render(db: Session, markdown: str, allowed: set[int] | None = None) -> str:
    """Rewrite valid tags to numbered links, strip invalid ones (+ visible
    note), style [unverified] markers, and append the Sources section."""
    bad = invalid_ids(db, markdown, allowed)
    order = [chunk_id for chunk_id in cited_ids(markdown) if chunk_id not in bad]
    chunks: dict[int, DocumentChunk] = {}
    if order:
        rows = db.scalars(select(DocumentChunk).where(DocumentChunk.id.in_(order)))
        chunks = {c.id: c for c in rows}
        order = [chunk_id for chunk_id in order if chunk_id in chunks]
    numbers = {chunk_id: n for n, chunk_id in enumerate(order, start=1)}

    def _sub(match: re.Match) -> str:
        chunk_id = int(match.group(1))
        if chunk_id in numbers:
            return f" [[{numbers[chunk_id]}]]({chunks[chunk_id].source_url})"
        return ""

    out = _TAG.sub(_sub, markdown)
    out = out.replace("[unverified]", _UNVERIFIED_BADGE)

    if order:
        lines = ["", "## Sources"]
        for chunk_id in order:
            chunk = chunks[chunk_id]
            date = str(chunk.published_at)[:10] if chunk.published_at else "n.d."
            lines.append(
                f"{numbers[chunk_id]}. [{chunk.title}]({chunk.source_url}) — {date} "
                f"(chunk {chunk_id})"
            )
        out += "\n".join(lines)
    if bad:
        out += _DEGRADE_NOTE
    return out
