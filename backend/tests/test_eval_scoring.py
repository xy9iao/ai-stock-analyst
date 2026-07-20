"""Tests for the regression set's scoring module (eval/scoring.py).

Pure functions, fully deterministic — no LLM, no DB. These are the executable
spec for the core scoring unit.
"""

import pytest

from eval.scoring import normalize, score_case, set_score, gate

FACTS = [
    {"label": "ticker", "any": ["NVDA"]},
    {"label": "price evidence", "any": ["price", "close", "%"]},
    {"label": "disclaimer", "any": ["not financial advice", "own research"]},
]


def test_normalize_folds_case_and_whitespace() -> None:
    assert normalize("  NVDA   dropped\n8%  ") == "nvda dropped 8%"


def test_full_coverage() -> None:
    memo = "NVDA's price fell 8%. This is not financial advice."
    result = score_case("c1", memo, FACTS)
    assert result.score == 1.0
    assert result.missed == []


def test_partial_coverage_reports_missed_labels() -> None:
    memo = "NVDA had a bad week."  # no price evidence, no disclaimer
    result = score_case("c1", memo, FACTS)
    assert result.score == pytest.approx(1 / 3)
    assert result.missed == ["price evidence", "disclaimer"]
    assert result.matched == ["ticker"]


def test_any_alternate_matches() -> None:
    memo = "nvda closed lower. do your own research."
    result = score_case("c1", memo, FACTS)  # "close" and "own research" via alternates
    assert result.score == 1.0


def test_matching_is_case_insensitive() -> None:
    result = score_case("c1", "NVDA PRICE — NOT FINANCIAL ADVICE", FACTS)
    assert result.score == 1.0


def test_must_not_violation_zeroes_case() -> None:
    memo = "NVDA price up. Not financial advice. This is guaranteed to rise."
    result = score_case("c1", memo, FACTS, must_not=["guaranteed", "risk-free"])
    assert result.score == 0.0
    assert result.violations == ["guaranteed"]


def test_empty_memo_scores_zero() -> None:
    assert score_case("c1", "", FACTS).score == 0.0


def test_set_score_is_mean() -> None:
    a = score_case("a", "NVDA price, not financial advice", FACTS)  # 1.0
    b = score_case("b", "nothing relevant", FACTS)  # 0.0
    assert set_score([a, b]) == pytest.approx(0.5)


def test_set_score_empty_is_zero() -> None:
    assert set_score([]) == 0.0


def test_gate_without_baseline_passes() -> None:
    assert gate(0.4, None, 0.05) is True


def test_gate_within_tolerance_passes() -> None:
    assert gate(0.76, 0.80, 0.05) is True


def test_gate_drop_beyond_tolerance_blocks() -> None:
    assert gate(0.70, 0.80, 0.05) is False


def test_gate_improvement_passes() -> None:
    assert gate(0.90, 0.80, 0.05) is True
