"""Key-fact coverage scoring for the research-agent regression set (13.6).

Pure functions, deterministic by construction: the gate must be more stable
than the non-deterministic system it measures, so there is no model, no
randomness, and no IO anywhere in this module.
"""

from dataclasses import dataclass


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    matched: list[str]  # labels of facts found in the memo
    missed: list[str]  # labels of facts absent — the diagnostic payload
    violations: list[str]  # must_not terms found; any one voids the case

    @property
    def score(self) -> float:
        if self.violations:
            return 0.0
        total = len(self.matched) + len(self.missed)
        return len(self.matched) / total if total else 0.0


def score_case(
    case_id: str,
    memo: str,
    key_facts: list[dict],
    must_not: tuple[str, ...] | list[str] = (),
) -> CaseScore:
    text = normalize(memo)
    matched: list[str] = []
    missed: list[str] = []
    for fact in key_facts:
        hit = any(normalize(alt) in text for alt in fact["any"])
        (matched if hit else missed).append(fact["label"])
    violations = [term for term in must_not if normalize(term) in text]
    return CaseScore(case_id, matched, missed, violations)


def set_score(results: list[CaseScore]) -> float:
    return sum(r.score for r in results) / len(results) if results else 0.0


def gate(score: float, baseline: float | None, tolerance: float) -> bool:
    """True = merge may proceed. No baseline yet -> vacuous pass (record one)."""
    if baseline is None:
        return True
    return score >= baseline - tolerance
