# Documentation

How this folder is organized.

- **[`roadmap.md`](roadmap.md)** — progress and the active phase's scope. **Single source of truth** for what phase we're in and what's in/out of scope. Check this before writing code.
- **[`planning/`](planning/)** — high-level design intent (not literal code layout): `charter.md`, `vision.md`, `requirements.md`, `user-stories.md`, `architecture.md`, `data-sources.md`, `ai-design.md`, `decisions.md`, `open-questions.md`. Each carries a dated v0-outcome/v1 status banner; **version scope itself lives in [`roadmap.md`](roadmap.md)**. Only `decisions.md` and `open-questions.md` are appended to as the project evolves.
- **[`guides/`](guides/)** — implementation reference, kept accurate as code changes: `backend.md`, `database.md`, `api.md`, `frontend.md`, `development-workflow.md`.
- **[`images/`](images/)** — screenshots referenced by the root README.

Build history by phase lives in **[`CHANGELOG.md`](../CHANGELOG.md)** in the repo root — the accurate, frozen record of what was actually built.

One-time planning/handoff documents that used to live in `docs/archive/` were removed at the v0 freeze (2026-07-02); their content was long since absorbed into `roadmap.md`, `CHANGELOG.md`, and `CLAUDE.md`, and the originals remain available in git history.
