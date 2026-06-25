# Documentation

How this folder is organized.

- **[`roadmap.md`](roadmap.md)** — progress and the current phase's detailed scope. **Single source of truth** for what phase we're in and what's in/out of scope. Check this before writing code.
- **[`planning/`](planning/)** — frozen high-level design, read for **intent** (not literal code layout): `charter.md`, `vision.md`, `requirements.md`, `user-stories.md`, `architecture.md`, `data-sources.md`, `ai-design.md`, `decisions.md`, `open-questions.md`. Only `decisions.md` and `open-questions.md` may still be appended to.
- **[`guides/`](guides/)** — implementation reference, kept accurate as code changes: `backend.md`, `database.md`, `development-workflow.md`. `api.md` to be added once the Phase 3 APIs exist.
- **[`archive/`](archive/)** — archived one-time handoff documents (`project-orientation.md`, `07 Roadmap.md`, `10 Implementation Plan.md`, `11 v0.md`, `phase-2-plan.md`, `phase-3-plan.md`). Their content has been absorbed into `roadmap.md`; kept frozen for provenance, not maintained.

Build history by phase lives in **[`CHANGELOG.md`](../CHANGELOG.md)** in the repo root.
