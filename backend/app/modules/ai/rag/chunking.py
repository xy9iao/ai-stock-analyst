"""Deterministic fixed-size chunking with overlap and boundary snapping (Phase 14).

Pure functions: same text -> same chunks, forever. Chunk identity is
(source_url, chunk_index), so determinism is what keeps citation IDs stable.
Parameters are regression-gated: changing them runs eval/ before merge.
"""

CHUNK_SIZE = 1800  # chars ≈ 450 tokens at the ~4 chars/token heuristic
CHUNK_OVERLAP = 200  # ~11% duplicated across neighbors — boundary-fact insurance

_SENTENCE_ENDS = (". ", "! ", "? ", ".\n", "!\n", "?\n")


def chunk_text(text: str, *, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into <=size-char chunks, consecutive chunks sharing ~overlap chars.

    Cuts prefer sentence ends, then whitespace, inside the last size//10 chars
    of each window; a hard cut only when the window has no boundary at all.
    """
    snap = size // 10
    if size <= overlap + snap:
        raise ValueError("size must exceed overlap + snap window (loop progress)")

    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        end = _snap_end(text, end - snap, end)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def _snap_end(text: str, zone: int, end: int) -> int:
    """Best cut position in [zone, end): sentence end > whitespace > hard cut."""
    best = -1
    for sep in _SENTENCE_ENDS:
        pos = text.rfind(sep, zone, end)
        if pos != -1:
            best = max(best, pos + len(sep))
    if best != -1:
        return best
    for i in range(end - 1, zone - 1, -1):
        if text[i].isspace():
            return i + 1
    return end
