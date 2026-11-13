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

Use a separate one-per-task assignment table with composite project-scoped foreign keys. Database constraints prevent moving or deleting assigned agents and cross-project associations, including direct SQL; deleting a task cascades its assignment. Adding or changing an assignment is permitted for pending tasks under the existing project lock. Removing it is permitted in any status so terminal records do not trap agent configurations; deleting the task also removes the association. Idempotent repeats produce no event. This is not a worker lease, scheduling mechanism, runtime status, security audit or proof of execution. Downgrade 0008 refuses to erase active assignments.

## 2026-11-13: Read-only ready-task snapshot

A single database query lists pending tasks without incomplete direct prerequisites; project and assignment filters and bounded pagination are available. This is advisory and does not claim, lock or schedule tasks. Offset pages can shift during concurrent writes and the list may be stale immediately. Manual completion retains its independent project-locked check. A reliable future worker scheduler will require transactional claims, leases, recovery and authorization rather than using this list as a queue.

## 2026-11-13: Explicit local provider connectivity probe

Use the official SDK adapter behind a one-shot local CLI with a fixed non-sensitive prompt, explicit model and billable-operation acknowledgement. Reject missing key/confirmation before client creation; cap output, disable retries and request storage, close the client and sanitize output/errors. Fix the SDK base URL to the official OpenAI API to prevent an accidental `OPENAI_BASE_URL` environment override from redirecting credentials; trusted proxy/certificate/logging environment remains part of the trust boundary. Do not expose a paid provider call on the unauthenticated HTTP API or connect it to task execution. No live call or credentials used. Account limits, actual billing, network connectivity, retention and production readiness remain unverified.

## 2026-11-13: Opt-in one-shot local text request

Add an explicitly invoked CLI using the provider adapter, with separate acknowledgement of remote data transfer and cost, bounded stdin and output tokens, no retries and sanitized failures. The model output is untrusted and displayed, never executed. Strip control/format characters to mitigate terminal escape sequences, at the cost of changing some Unicode text. No task, HTTP endpoint, automatic agent or model tool access is involved. Command output may be retained by the shell or caller; provider retention and cost remain external. Real-provider and platform testing remain unverified. This does not establish production-safe authorization or cost controls.

## 2026-11-13: Initial manual assigned-task text execution

Implement a one-shot, operator-invoked OpenAI text worker, not autonomous orchestration. Claim a pending, dependency-ready task with an assigned same-project agent under the project lock; a partial unique index enforces at most one unresolved run per task. Save only metadata and token counts, never prompt, output or secrets. Provider errors, timeouts and crashes have unknown remote/billing outcomes; do not automatically retry or expire claims. Explicit operator resolution requires stopping and investigating the worker, but cannot cancel a remote request. Output is untrusted, printed only and does not complete the task; no tools, shell or browser are enabled. Editing task and agent data while a run executes is allowed; it uses a snapshot, so results can become stale. Metadata history restricts task/agent deletion until administratively handled. There is no authentication, sandbox, job manager, retention UI, cost control or live-provider verification. This narrow step is not a complete agent lifecycle or production-ready scheduler.

## 2026-11-13: Explicit bounded first-run batch

Add a one-shot sequential project-scoped CLI that selects active-project ready tasks assigned to configured OpenAI agents with no run history. Require an explicit 1–20 request cap and separate cost and transfer confirmations. The selection is advisory; the worker revalidates project state and no-history inside the existing project lock and unique active-run claim before each call, avoiding duplicate batch attempts if another worker finishes between selection and claim. Any rejection or uncertain result stops the batch; later invocations never retry existing history. Human task completion remains independent. At that checkpoint this was not a persistent scheduler, global concurrency limit, cost budget or safe untrusted code sandbox; the subsequent capacity decision adds a claim limit. Provider traffic remains opt-in and unverified live.

## 2026-11-13: Advisory text-worker heartbeat

Add nullable heartbeat timestamps to run metadata and a best-effort periodic write while a local text request is running. Legacy records remain unknown. An API derives freshness from database timestamps and API host clock, with unknown for significant future skew; no heartbeat is interpreted as proof of process or provider health. No automatic claim release, retry or restart is allowed on staleness because remote execution and billing can be ambiguous. The loop stops on a DB write failure but does not cancel the provider request. This is limited observability, not a complete agent lifecycle or lease mechanism; authenticated orchestration and safe recovery remain future work.

## 2026-11-13: Shared unresolved-run capacity

Serialize application claims across projects with a PostgreSQL singleton row lock or SQLite immediate write transaction before the project lock. Count running and uncertain runs under that lock and reject claims at 20; retain capacity until explicit resolution. A partial unique index prevents multiple unresolved runs for the same agent independently of API checks. Migration 0011 refuses duplicate unresolved agent histories and downgrade refuses unresolved runs. Direct SQL, mistaken manual resolution of a live worker and clock/remote uncertainty remain outside the guarantee. This limits claims rather than OS processes, agent configuration count, external provider activity or spend.

## 2026-11-13: Optional local shared API bearer gate

As an interim local-only safeguard, accept a configured high-entropy shared bearer secret for `/api` routes; absent configuration remains unauthenticated for compatibility, while an explicitly empty or invalid secret fails closed at startup. Use constant-time comparison and avoid token URLs, persistent browser storage and reflected errors; health and schema are public. The frontend stores the token in memory only and sends it solely to same-origin relative API URLs. This is not user authentication, RBAC, rate limiting, TLS, secret rotation service or a substitute for database/filesystem access control. Workers directly access the DB, and XSS, hostile local processes and extensions remain threats. Evaluate mature identity/session libraries separately before production or remote access.
