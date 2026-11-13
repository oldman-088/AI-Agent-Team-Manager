# Technical decisions

## 2026-11-13: Phase 0 baseline

- Keep the existing SQLite/static prototype intact and explicitly unsupported for production. No data migration is claimed. Replace it incrementally, with an explicit migration decision before removal.
- Target FastAPI/Pydantic, SQLAlchemy/Alembic and PostgreSQL, and React/TypeScript/Vite for Phase 1 as requested; exact versions and licenses remain to be reviewed. Do not add Redis without a demonstrated need.
- Prefer Playwright for future browser control and E2E coverage; no browser dependency or installation is yet present.
- Prefer official provider SDKs behind AATM-owned interfaces initially. Framework and provider selections remain unvalidated; see research.
- No application license is selected: the repository owner has not supplied one. Do not invent a license grant. Verify third-party obligations before distributing dependencies.
- Work on the session's existing branch; platform constraints prohibit creating or switching branches. A PR can be prepared from this branch, subject to review and branch rules.

## 2026-11-13: Planning tasks before execution

A small Phase 4 planning-task slice is implemented in parallel with unfinished Phases 0–3 because it is independently useful and requires no provider credentials or unsafe execution. This does not skip or complete those phases. Only pending/cancelled states exist; assignment, dependency scheduling, execution and review are deliberately deferred until their safety and concurrency invariants are designed. Project deletion is restricted while tasks exist to avoid silent loss.

## 2026-11-13: Narrow provider interface

Adopt the official OpenAI Python SDK behind a small asynchronous text-completion protocol. Provider credentials are passed explicitly by the caller and are not stored; output token count is bounded, SDK retries disabled and upstream error details suppressed. `store=false` is requested but does not establish a complete retention guarantee. This is a library-level integration only, not an exposed API, credential manager, agent execution system or live-tested provider. Streaming, tools, model discovery and costs remain future work. Other provider SDKs remain candidates.
