# Workflow report

Last updated: 2026-11-13T18:33:06+00:00

## Completion indicator

**13.3% of acceptance criteria verified**: 4 of 30 equally weighted binary criteria (2–5). Partial criteria receive zero; this is not an effort or delivery estimate. See [Arabic progress report](تقرير_التقدم.md).

## Current work

Added a metadata-only task activity history, persisted in the same transaction as selected task and dependency changes. The dashboard displays recent events. The 0007 downgrade refuses to discard nonempty history. Events have no authenticated actor, are not tamper-proof, and do not form a complete security audit; only API-mediated task operations after migration are covered. No task content or secrets are copied to events. Deleting referenced tasks/projects detaches their IDs rather than allowing ID reuse to misattribute history.

## Verification and fixes

- Backend: 11 tests passed on SQLite, including rollback on event failure, idempotence, detach behavior and downgrade protection. First test run exposed the intended downgrade guard; updated the disposable test to check it before explicitly clearing test data. Starlette httpx deprecation warning remains.
- Frontend: typecheck, 13 tests and build passed; npm audit found zero vulnerabilities. Initial typecheck failed on a missing import; fixed and reran.
- Documentation inventory and diff check passed before report update. All PR checks passed at `875d083`: [PostgreSQL activity tests](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43476706411), [Chromium activity E2E](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43476706466), [frontend](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43476706255), [prototype matrix](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43476706340), and [CodeQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43476706294). Later commits need their own checks.

## Limitations and next actions

Project license remains unselected. PostgreSQL is unavailable locally; the activity tests passed in CI. Design authenticated and tamper-resistant auditing and safe execution. Agent execution, automatic scheduling, authentication, comprehensive audit and most platform capabilities are incomplete. See JSON report for file inventory; duration unknown.

## Dependency UI checkpoint

Added localized task dependency inspection, addition and removal, and readiness snapshot with blocker IDs. Selection is limited to the first 100 loaded tasks; server revalidates changes and completion. Frontend typecheck, 15 tests, build and npm audit passed locally. Browser CI initially failed due to a label selector and a PUT missing the JSON content type required by the server guard; both were corrected and regression-tested. All PR checks passed at `8829de9`: [Chromium](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43480400100), [PostgreSQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43480400177), [frontend](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43480400278), [matrix](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43480400193) and [CodeQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43480400181). Later commits require their own checks. Acceptance remains 4/30.

## Planning assignment checkpoint

Added one planning assignment per task with project-scoped database foreign keys, a manual API and localized UI. It does not start an agent. Only pending task assignments can be changed; assigned agents cannot move or be deleted. At that checkpoint terminal assignments remained until task deletion; the later checkpoint below removes that restriction. Downgrade 0008 refuses to drop assignments. SQLite backend tests passed (11); frontend typecheck, 15 tests and build passed before final copy and E2E changes. All PR checks passed at `520f0ae`: [PostgreSQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43481281322), [Chromium](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43481281202), [frontend](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43481281205), [prototype matrix](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43481281265) and [CodeQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43481281417). Later commits require separate verification. Acceptance remains 4/30.

## Terminal unassignment and concurrency checkpoint

Assignments can now be removed from completed or cancelled tasks without deleting them; adding or changing an agent still requires a pending task. Added a concurrent assignment-versus-agent-move test. SQLite backend tests (11), frontend typecheck, 15 tests and build passed locally; npm audit found zero vulnerabilities. All PR checks passed at `4158e99`: [PostgreSQL race](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43482199909), [Chromium unassignment](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43482200327), [frontend](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43482199956), [prototype matrix](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43482199947) and [CodeQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43482200332). Later commits need separate verification. This is still planning only, not execution. Acceptance remains 4/30.

## Ready planning task snapshot checkpoint

Added a read-only ready task query with project and assignment filters and bounded offset pagination, plus localized dashboard display. It is a snapshot, not an execution queue or reservation; completion rechecks under the project lock. SQLite backend tests (11), frontend typecheck, 16 tests and build passed locally; npm audit zero vulnerabilities. Initial browser CI failed because the existing test matched both similarly named regions; using the exact accessible name fixed it. All PR checks passed at `9b14e10`: [PostgreSQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43483208968), [Chromium](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43483209198), [frontend](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43483208920), [prototype matrix](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43483208470) and [CodeQL](https://github.com/oldman-088/AI-Agent-Team-Manager/actions/runs/43483208450). Later commits need separate verification. Acceptance remains 4/30.

## Provider connectivity probe checkpoint

Moved from planning to a local, explicitly confirmed, potentially billable OpenAI probe. The CLI uses a fixed prompt, output limit, no retries, official API base URL and sanitized output; no HTTP paid endpoint is exposed. Backend tests: 15 passed on SQLite with mocks; no real credentials or live call. GitHub CI pending. This is not task execution or provider validation; return to planning improvements later. Acceptance remains 4/30.
