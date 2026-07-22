# AGENTS.md

**[`CLAUDE.md`](CLAUDE.md) is the single source of project rules for every coding assistant** (Codex, Claude, or any other) — read it first and follow it in full. This file is a pointer, not a second rulebook; it restates only the three non-negotiables so they can never be missed:

1. **Sole author, no AI attribution.** This is the developer's personal solo project. Author every commit, PR, and issue as the developer alone — **never** add a `Co-Authored-By` trailer or any AI/assistant attribution. Applies to *any* assistant, overriding default co-authorship behavior.
2. **Data & secrets boundary.** The backend owns everything external (database, market/news APIs, the LLM, all secrets); the frontend is presentation-only and talks to nothing but the backend REST API. Secrets live only in the gitignored root `.env` — never commit real secrets.
3. **PR workflow + phase discipline.** Every change lands on a branch → PR → CI gates (backend `ruff` + `pytest`; frontend `typecheck`/`lint`/`test`/`build`). v1 is complete; the project is in **demand-gated maintenance** — any change to prompts, models, or retrieval/compression parameters must pass `backend/eval/` (`uv run python -m eval.run`, `--citations`, `--poisoned`) before merge, and new features are built only when the same need recurs.

If this file and `CLAUDE.md` ever diverge, **`CLAUDE.md` wins** and this file must be reverted to a pointer.
