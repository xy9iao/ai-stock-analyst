"""Regression runner: execute every case through the real agent loop and gate on score.

Direct function calls into `run_research` — no HTTP, no server. Each run spends real
LLM tokens (~20 cases x ~6 calls), which is why this is local-only and never CI.
A crashed case scores 0 and the run continues; the gate decides the exit code.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from app.core.database import SessionLocal
from app.modules.ai.agent.loop import run_research
from eval.scoring import CaseScore, gate, score_case, set_score

CASES_PATH = Path(__file__).parent / "cases.json"
BASELINE_PATH = Path(__file__).parent / "baseline.json"
SESSION_ID = "eval"
DEFAULT_TOLERANCE = 0.05


def load_baseline() -> dict | None:
    if not BASELINE_PATH.exists():
        return None
    return json.loads(BASELINE_PATH.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description="Research-agent regression set (13.6)")
    parser.add_argument(
        "--record", action="store_true", help="accept the current score as the new baseline"
    )
    parser.add_argument("--only", help="run a single case id (authoring/debugging)")
    args = parser.parse_args()

    cases = json.loads(CASES_PATH.read_text())["cases"]
    if args.only:
        cases = [c for c in cases if c["id"] == args.only]
        if not cases:
            print(f"no case with id {args.only!r}")
            return 2

    results: list[CaseScore] = []
    notes: dict[str, str] = {}
    db = SessionLocal()
    try:
        for case in cases:
            try:
                run = run_research(db, SESSION_ID, case["query"])
                result = score_case(
                    case["id"], run.memo, case["key_facts"], case.get("must_not", ())
                )
                notes[case["id"]] = f"steps={run.steps}" + (" LIMIT" if run.step_limit_hit else "")
            except Exception as exc:  # a broken case must not sink the whole run
                result = score_case(case["id"], "", case["key_facts"], ())
                notes[case["id"]] = f"CRASHED: {exc}"
            results.append(result)
            print(f"  {result.case_id:32s} {result.score:5.2f}  {notes[result.case_id]}")
            for label in result.missed:
                print(f"      missed: {label}")
            for term in result.violations:
                print(f"      VIOLATION: {term!r}")
    finally:
        db.close()

    score = set_score(results)
    baseline = load_baseline()
    print(f"\nset score: {score:.3f}  over {len(results)} cases")

    if args.record:
        BASELINE_PATH.write_text(
            json.dumps(
                {
                    "score": round(score, 3),
                    "tolerance": DEFAULT_TOLERANCE,
                    "recorded": str(date.today()),
                    "cases": len(results),
                },
                indent=2,
            )
            + "\n"
        )
        print(f"baseline recorded: {score:.3f} (tolerance {DEFAULT_TOLERANCE})")
        return 0

    if baseline is None:
        print("no baseline yet — run with --record to set one. PASS (vacuous)")
        return 0

    passed = gate(score, baseline["score"], baseline["tolerance"])
    print(
        f"baseline {baseline['score']:.3f} (recorded {baseline['recorded']}, "
        f"tolerance {baseline['tolerance']}): {'PASS' if passed else 'FAIL - blocks merge'}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
