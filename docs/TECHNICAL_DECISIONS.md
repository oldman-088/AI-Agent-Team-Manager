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

## 2026-11-13: Task dependencies as planning data

Implement same-project dependency edges with database-enforced membership and an explicit 10,000-edge per-project limit. Serialize graph changes per project via PostgreSQL row locks; SQLite uses a database-level immediate write transaction. Reject cyclic and self dependencies and refuse deletion of referenced tasks. API graph edits are serialized, but arbitrary direct SQL can bypass the cycle check. No automatic scheduling, ready-state derivation or execution is implied. Tests cover opposing concurrent edits; PostgreSQL CI verification is required separately.

## 2026-11-13: Manual task completion and readiness

A human may explicitly mark a task completed after its direct dependencies are completed. This records no execution, identity, evidence or review and must not be presented as an agent action. Readiness is informational; completion checks again while holding the same lock used for dependency edits. Cancelled prerequisites block completion. Completed tasks cannot acquire new dependencies or be cancelled. Removing an edge remains permitted for cleanup; this is not an audit trail. Downgrading the new state constraint refuses to rewrite completed rows.

## 2026-11-13: Minimal operational task history

Record selected task and dependency events transactionally, without copying names, prompts, credentials or other user content. Null references when a task or project is deleted rather than misattribute history if an ID is reused. Event history is not an authenticated, immutable or complete audit log, has no retention policy, and covers only API-mediated changes after migration 0007. The 0007 downgrade rejects nonempty history to prevent silent loss. Production audit, identity, retention and authorization require separate design.

## 2026-11-13: Planning-only task assignments

Use a separate one-per-task assignment table with composite project-scoped foreign keys. Database constraints prevent moving or deleting assigned agents and cross-project associations, including direct SQL; deleting a task cascades its assignment. Changes are permitted for pending tasks under the existing project lock. Terminal assignments are retained and cannot be cleared through the API; deleting the task removes the association, a deliberate current limitation. Idempotent repeats produce no event. This is not a worker lease, scheduling mechanism, runtime status, security audit or proof of execution. Downgrade 0008 refuses to erase active assignments.
