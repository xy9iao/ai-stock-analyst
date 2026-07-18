"""Phase 13 regression set: key-fact coverage gate for the research agent.

Local-run only (real LLM spend) — never wired into CI. One command, from backend/:

    uv run python -m eval.run            # run the set, compare against baseline
    uv run python -m eval.run --record   # accept the current score as the new baseline
"""
