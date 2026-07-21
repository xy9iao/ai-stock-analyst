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
from eval.citation_check import check_citation
from eval.scoring import CaseScore, gate, score_case, set_score

CASES_PATH = Path(__file__).parent / "cases.json"
CITATION_CASES_PATH = Path(__file__).parent / "citation_cases.json"
POISONED_CASES_PATH = Path(__file__).parent / "poisoned_cases.json"
BASELINE_PATH = Path(__file__).parent / "baseline.json"
FAILURES_PATH = Path(__file__).parent / ".last_failures.md"  # gitignored diagnostics
SESSION_ID = "eval"
DEFAULT_TOLERANCE = 0.05


def load_baseline() -> dict | None:
    if not BASELINE_PATH.exists():
        return None
    return json.loads(BASELINE_PATH.read_text())


def write_failures(failing: list[tuple[str, str]]) -> None:
    """Persist imperfect cases' memos so failures are inspectable, not mysteries."""
    if not failing:
        FAILURES_PATH.unlink(missing_ok=True)
        return
    parts = ["# Imperfect cases, last run\n"]
    for case_id, memo in failing:
        parts.append(f"\n---\n\n## {case_id}\n\n{memo}\n")
    FAILURES_PATH.write_text("".join(parts))
    print(f"imperfect-case memos written to {FAILURES_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Research-agent regression set (13.6)")
    parser.add_argument(
        "--record", action="store_true", help="accept the current score as the new baseline"
    )
    parser.add_argument("--only", help="run a single case id (authoring/debugging)")
    parser.add_argument(
        "--citations", action="store_true", help="run the citation cases instead of coverage"
    )
    parser.add_argument(
        "--poisoned", action="store_true", help="run the poisoned-chunk injection cases"
    )
    args = parser.parse_args()

    if args.citations:
        return run_citation_cases(args.only)
    if args.poisoned:
        return run_poisoned_cases(args.only)

    cases = json.loads(CASES_PATH.read_text())["cases"]
    if args.only:
        cases = [c for c in cases if c["id"] == args.only]
        if not cases:
            print(f"no case with id {args.only!r}")
            return 2

    results: list[CaseScore] = []
    notes: dict[str, str] = {}
    failing: list[tuple[str, str]] = []
    db = SessionLocal()
    try:
        for case in cases:
            try:
                run = run_research(db, SESSION_ID, case["query"])
                result = score_case(
                    case["id"], run.memo, case["key_facts"], case.get("must_not", ())
                )
                notes[case["id"]] = f"steps={run.steps}" + (" LIMIT" if run.step_limit_hit else "")
                if result.score < 1.0:
                    failing.append((case["id"], run.memo))
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

    write_failures(failing)
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


def run_citation_cases(only: str | None = None) -> int:
    """Citation gate: every case must pass (presence + support). Exit 1 on any fail."""
    cases = json.loads(CITATION_CASES_PATH.read_text())["cases"]
    if only:
        cases = [c for c in cases if c["id"] == only]
        if not cases:
            print(f"no citation case with id {only!r}")
            return 2

    failures = 0
    failing: list[tuple[str, str]] = []
    db = SessionLocal()
    try:
        for case in cases:
            run = None
            try:
                run = run_research(db, SESSION_ID, case["query"])
                result = check_citation(db, case["id"], run.memo, case["cited_atom"])
                detail = (
                    f"atom_found={result.atom_found} cited={result.cited} "
                    f"supported={result.supported} memo_tags={result.memo_tag_count} "
                    f"steps={run.steps}"
                )
            except Exception as exc:
                result = None
                detail = f"CRASHED: {exc}"
            passed = result is not None and result.passed
            failures += 0 if passed else 1
            print(f"  {case['id']:32s} {'PASS' if passed else 'FAIL'}  {detail}")
            if result is not None and not passed:
                for line in result.atom_lines[:3]:
                    print(f"      atom line: {line.strip()[:120]}")
                if run is not None:
                    failing.append((case["id"], run.memo))
    finally:
        db.close()

    write_failures(failing)
    print(f"\ncitation cases: {len(cases) - failures}/{len(cases)} passed")
    return 0 if failures == 0 else 1


def run_poisoned_cases(only: str | None = None) -> int:
    """Injection gate: plant a poisoned chunk, run the query, grep for canaries.

    Pass = no canary appears in the memo (deterministic compliance check —
    subtle bias is out of scope; lying content is citations' problem).
    Fixtures are inserted with real embeddings and removed afterwards.
    """
    from sqlalchemy import delete

    from app.models import DocumentChunk
    from app.modules.ai.rag.embeddings_client import embed_texts
    from eval.scoring import normalize

    cases = json.loads(POISONED_CASES_PATH.read_text())["cases"]
    if only:
        cases = [c for c in cases if c["id"] == only]
        if not cases:
            print(f"no poisoned case with id {only!r}")
            return 2

    failures = 0
    failing: list[tuple[str, str]] = []
    db = SessionLocal()
    try:
        for case in cases:
            url = f"https://eval.poison/{case['id']}"
            db.execute(delete(DocumentChunk).where(DocumentChunk.source_url == url))
            vector = embed_texts([case["content"]], db=db)[0]
            db.add(
                DocumentChunk(
                    source_url=url,
                    title=case["title"],
                    ticker="NVDA",
                    chunk_index=0,
                    content=case["content"],
                    embedding=vector,
                )
            )
            db.commit()
            try:
                run = run_research(db, SESSION_ID, case["query"])
                memo = normalize(run.memo)
                hits = [c for c in case["canaries"] if normalize(c) in memo]
                passed = not hits
                detail = f"canaries_found={hits} steps={run.steps}"
                if not passed:
                    failing.append((case["id"], run.memo))
            except Exception as exc:
                passed = False
                detail = f"CRASHED: {exc}"
            finally:
                db.execute(delete(DocumentChunk).where(DocumentChunk.source_url == url))
                db.commit()
            failures += 0 if passed else 1
            print(f"  {case['id']:32s} {'PASS' if passed else 'FAIL'}  {detail}")
    finally:
        db.close()

    write_failures(failing)
    print(f"\npoisoned cases: {len(cases) - failures}/{len(cases)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
