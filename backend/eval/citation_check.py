"""Mechanical checker for citation eval cases (Phase 14).

A case passes when BOTH hold on the RAW memo (pre-render, where [chunk:N]
tags are still visible):
  1. presence  — the line containing the expected atom carries a [chunk:N] tag
  2. support   — at least one of that line's cited chunks contains the atom

Deterministic string work only — no model judges a model. Support-by-atom-
containment verifies the fact is in the chunk, not that the chunk's meaning
endorses the claim (known, accepted depth for a maintenance gate).
"""

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from eval.scoring import normalize

_TAG = re.compile(r"\[chunk:(\d+)\]")


@dataclass(frozen=True)
class CitationResult:
    case_id: str
    atom_found: bool  # the atom appears in the memo at all
    cited: bool  # at least one atom-bearing line carries a [chunk:N] tag
    supported: bool  # some atom-bearing line's cited chunk contains the atom
    memo_tag_count: int  # total [chunk:N] tags anywhere (diagnostic)
    atom_lines: tuple[str, ...]  # atom-bearing lines, for failure diagnosis

    @property
    def passed(self) -> bool:
        return self.atom_found and self.cited and self.supported


def check_citation(db: Session, case_id: str, memo: str, cited_atom: str) -> CitationResult:
    """Pass if ANY atom-bearing line is cited by a chunk containing the atom.

    Any-line (not first-line) semantics: atoms recur across a memo — section
    headings, tables, prose — and headings legitimately carry no tags. The
    claim is 'this fact is cited somewhere it is stated', not 'everywhere'.
    """
    atom = normalize(cited_atom)
    memo_tag_count = len(_TAG.findall(memo))
    lines = tuple(ln for ln in memo.splitlines() if atom in normalize(ln))
    if not lines:
        return CitationResult(case_id, False, False, False, memo_tag_count, ())

    cited = False
    for line in lines:
        chunk_ids = [int(m) for m in _TAG.findall(line)]
        if not chunk_ids:
            continue
        cited = True
        contents = db.scalars(
            select(DocumentChunk.content).where(DocumentChunk.id.in_(chunk_ids))
        ).all()
        if any(atom in normalize(content) for content in contents):
            return CitationResult(case_id, True, True, True, memo_tag_count, lines)
    return CitationResult(case_id, True, cited, False, memo_tag_count, lines)
