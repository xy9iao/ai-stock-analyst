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
    cited: bool  # its line carries at least one [chunk:N] tag
    supported: bool  # a cited chunk actually contains the atom

    @property
    def passed(self) -> bool:
        return self.atom_found and self.cited and self.supported


def check_citation(db: Session, case_id: str, memo: str, cited_atom: str) -> CitationResult:
    atom = normalize(cited_atom)
    line = next((ln for ln in memo.splitlines() if atom in normalize(ln)), None)
    if line is None:
        return CitationResult(case_id, atom_found=False, cited=False, supported=False)

    chunk_ids = [int(m) for m in _TAG.findall(line)]
    if not chunk_ids:
        return CitationResult(case_id, atom_found=True, cited=False, supported=False)

    contents = db.scalars(
        select(DocumentChunk.content).where(DocumentChunk.id.in_(chunk_ids))
    ).all()
    supported = any(atom in normalize(content) for content in contents)
    return CitationResult(case_id, atom_found=True, cited=True, supported=supported)
