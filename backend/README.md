# Backend foundation

Python 3.11+. From this directory create a virtual environment, then `pip install -e ".[test]"`. Set `AATM_DATABASE_URL` to a dedicated PostgreSQL database URL using SQLAlchemy's `postgresql+psycopg://` scheme. Use a local secret store or environment variables for credentials; never commit the URL if it contains credentials. Run `alembic upgrade head`, then `uvicorn app.main:app --host 127.0.0.1 --port 8001`. See `/docs`, `/health/live` and `/health/ready`. Readiness checks connectivity, not migration version. Missing configuration or an unreachable database returns 503 without exposing details.

Test with `pytest`; to exercise PostgreSQL migration upgrade/downgrade set `AATM_TEST_DATABASE_URL` to an **empty disposable database**. The test drops its `projects` table; never point it at valuable data. Without that variable SQLite is only a local smoke test. The initial schema and health probes do not implement project management or migrate the old SQLite prototype. No authentication is implemented: use loopback only and do not expose this service publicly.

## Project API

After migrations: `GET /api/projects` lists up to 100 records (`limit` 1–100, `offset` 0–1000000); `POST /api/projects` accepts `name`, optional `description`, and optional `status`. `GET`, `PATCH`, and `DELETE /api/projects/{id}` retrieve, update, and delete a record. Status values are `planned`, `active`, `paused`, `completed`, and `archived`. Deletes are permanent. The API currently stores only name, description, and status; it does not connect repositories, run agents, isolate projects, or implement full project management. Legacy prototype data is separate.

A localhost Host allowlist and origin/content-type checks reduce browser-based DNS rebinding and cross-origin write risks. They do not authenticate local users or protect against malicious local processes. Do not expose this API publicly, use it with sensitive data, or treat it as production-ready. The Vite proxy must be accessed via localhost or 127.0.0.1 for these checks.

## Agent configuration registry

`GET /api/agents` lists configurations with bounded `limit` and `offset`; `POST /api/agents` creates one with `name` and `role`, plus optional `description`, `instructions`, `provider`, `model` and `project_id`. `GET`, `PATCH`, and `DELETE /api/agents/{id}` retrieve, edit, or permanently delete a configuration; `project_id: null` unassigns it. Deleting a project unassigns its agents. Provider and model are labels only; they do not configure credentials or verify availability. `execution_status` is always `not_implemented`: there are no running processes, lifecycle controls, concurrency guarantees, heartbeat, cost tracking or execution history. Do not put credentials or sensitive information in agent instructions or other fields; records are stored in plaintext in the database. API and database are unauthenticated and local-only.

## Planning task API

`GET /api/tasks` lists tasks with optional `project_id`, `limit` and `offset` (same bounds as projects); `POST /api/tasks` accepts `project_id`, `title`, and optional `description`. `GET`, `PATCH`, and `DELETE /api/tasks/{id}` retrieve, edit title/description, or permanently delete a task. `POST /api/tasks/{id}/cancel` with a JSON body (for example `{}`) marks a pending task cancelled; repeating it is safe. Cancellation does not stop an execution process. Only `pending`, `cancelled`, and manually asserted `completed` states are supported. Agent assignment, dependency-based scheduling, execution, priority, timestamps, artifacts, review and recovery do not exist yet. Projects with tasks cannot be deleted: delete their tasks explicitly first; the API returns 409 instead of silently deleting them. Records are plaintext; do not store secrets.

## Provider adapter (development only)

`app.providers.openai_adapter.OpenAIProvider` implements a narrow asynchronous text-only provider contract using the official OpenAI SDK. Construct it with `OpenAIProvider.from_api_key(key)`, call `complete(CompletionRequest(model, prompt))`, and close it when done. It limits output tokens, requests `store=False`, disables automatic SDK retries and suppresses upstream error details. These measures do not guarantee zero retention, costs, or complete secrecy. The caller is responsible for securely obtaining credentials, authorization, data handling and rate/cost controls. Do not place credentials in project records, instructions, source, or logs. There is currently no provider UI, endpoint, secret manager, model discovery, streaming, tool calling, cost estimation or agent execution. Only mocked SDK/HTTP tests have run; no live OpenAI call or authentication has been verified.

## Task dependency API

`GET /api/tasks/{id}/dependencies` lists task IDs that must precede a task. `PUT /api/tasks/{id}/dependencies/{dependency_id}` adds an edge (JSON content type required; `{}` is acceptable), and `DELETE` at the same path removes it. An edge must connect two distinct tasks in the same project; duplicate additions are idempotent. Cycles are rejected with 409, and deleting tasks with edges requires removing the edges first. Each project is limited to 10,000 edges. PostgreSQL serializes dependency changes using a project row lock; SQLite uses `BEGIN IMMEDIATE`. Other database engines are not supported for graph changes. Database composite foreign keys enforce same-project membership. These guarantees assume modifications use this API and SQLite foreign keys remain enabled; arbitrary direct database changes can bypass application-level cycle checks. A dependency graph is planning data only: it does not schedule work, assign agents, or execute tasks. Readiness is a snapshot; completion is rechecked under a lock.

### Readiness and manual completion

`GET /api/tasks/{id}/readiness` returns the task status, a `ready` boolean, and IDs of dependencies that are not completed. This is a display snapshot, not a task claim or a promise that later execution will be allowed. `POST /api/tasks/{id}/complete` (JSON `{}`) records the user's **manual assertion** of completion only when all direct dependencies are completed; it does not run an agent or verify deliverables. A cancelled prerequisite blocks completion; cancelled tasks cannot be completed, and completed tasks cannot be cancelled. Both completion and dependency edits are serialized with the project lock. Completed tasks cannot gain new dependencies; removing existing edges is permitted, so this is not an immutable audit trail. No completion actor, execution record or review is stored yet. Database migration 0006 refuses to downgrade while completed tasks exist rather than silently altering them: back up and resolve such data explicitly before downgrading. Do not run downgrades against valuable data without a verified backup.

## Task activity (limited operational history)

`GET /api/events` lists the latest 100 metadata-only task events (optional `project_id`, `limit` and `offset`, with the same bounds as other lists). It records task create/update/delete, cancellation, manual completion and dependency add/remove in the same database transaction as the change. No title, description, instructions, prompt or credential is copied into the event. Repeated idempotent operations do not create duplicate transition events. When a referenced task or project is deleted, corresponding IDs become null; events remain but are detached to avoid association with reused IDs. Database timestamps reflect database timestamp settings and may lack timezone information in SQLite.

This is **not** a security audit log: it has no authenticated actor, immutable storage, comprehensive event coverage, retention policy or protection against a local database administrator. Existing records before the migration are not backfilled. The service remains unauthenticated and local-only. The 0007 downgrade refuses to delete existing event history; back up and resolve it explicitly before downgrading. Database changes made outside the API are not recorded.

## Planning assignments

`GET /api/tasks/{id}/assignment` returns the assigned agent configuration ID or null. `PUT` with `{"agent_id": 123}` assigns it; `{"agent_id": null}` removes the assignment. This is a **manual planning association only**, not scheduling, execution, a running agent, or verification. Only pending tasks may receive or change an assignment; removal is also allowed after completion or cancellation. A repeated unchanged request is idempotent. The agent must belong to the same project. Database foreign keys enforce project consistency and prevent deleting or moving an assigned agent; unassign the agent first, or delete the task (which removes its assignment). Removing a terminal assignment does not reopen the task. Migration 0008 refuses downgrade while assignments exist. Activity events record the assignment change without agent identity and are not an authenticated audit log.

## Ready planning tasks

`GET /api/tasks/ready` returns a paginated snapshot of pending tasks whose direct prerequisites are all completed. A cancelled or pending prerequisite blocks readiness; a task without prerequisites is ready. Optional `project_id` scopes the result, and `assigned_only=true` restricts it to tasks with a planning assignment. Results are ordered by task ID, with `limit` 1–100 (default 100) and `offset` 0–1000000. Offset pagination can shift under concurrent changes. The result is informational: it is not a claim, reservation, queue, worker, execution authorization, or proof of work; it can be stale immediately. Manual completion rechecks dependencies while holding the project lock.

## Optional, billable OpenAI connectivity probe

The local CLI is deliberately **not an API endpoint**: this application has no authentication, so exposing a billable remote call over its HTTP interface would be unsafe. To run it yourself, supply `OPENAI_API_KEY` through your local process environment (never as a command argument, in Git, or in a ticket), then from `backend` run:

```sh
python -m app.provider_probe --model YOUR_MODEL_ID --confirm-billable
```

The model ID must be available to your account. This sends the fixed prompt “Reply with the single word OK.” to OpenAI and may incur charges; the explicit flag is required. The request is limited to 32 output tokens, has a 30-second SDK timeout, no automatic retries, no tools and `store=false`. `store=false` does not guarantee zero provider retention. The SDK is configured with the official OpenAI API base URL rather than accepting `OPENAI_BASE_URL`; trusted proxy, certificate and SDK logging environment configuration still matters. Do not enable verbose HTTP/SDK logs with production credentials. No result text or credential is deliberately printed or persisted by this command; token counts may be printed if provided. Errors are sanitized. This is not a task execution or provider integration with the dashboard. It has only been tested with mocks; no live request was made, so real network connectivity, account permissions, model availability, billing and actual provider behavior are unverified.

## Optional one-shot text completion (local CLI)

This is separate from tasks and agents, and is not exposed through HTTP. Set `OPENAI_API_KEY` in your process environment and pass a user-provided model ID; input is read from standard input until EOF, not from command-line arguments. Example using a **non-sensitive** local file:

```sh
python -m app.provider_text --model YOUR_MODEL_ID --confirm-billable --confirm-data-transfer < prompt.txt
```

Both flags are required before input is read or the client is created. The full input (maximum 20,000 characters) is sent to OpenAI, potentially incurs charges, and must not contain credentials or private material you are not authorized to share. Upstream retention policies still apply even with `store=false`; read the provider's current terms. The response is intentionally printed to stdout, so terminal scrollback, shell redirection and downstream programs may retain it; token usage is printed to stderr when provided. Do not treat output as trusted instructions or execute it automatically. Unicode control and format characters are stripped before display (which can alter text, including some emoji and bidirectional formatting); output is truncated at 100,000 characters. Errors are sanitized, retries disabled, and output tokens capped at 512. The command does not persist content itself, but local environment, proxies, SDK logs, shell history, and the remote provider are separate trust boundaries. Never pass secrets in flags or enable verbose transport logging. Tests use mocked clients; no real account, request, billing, or platform compatibility has been verified.

## Manual assigned-task text worker (initial execution slice)

This worker is a **local, explicitly invoked, one-shot text generation**, not an autonomous agent process, scheduler, browser, shell, QA system or task completion verifier. It sends the assigned agent's role and instructions and the task title and description to OpenAI. Ensure you are authorized to send all of that content and that it contains no secrets or sensitive data you cannot disclose. `store=false` is requested but does not guarantee zero provider retention. Requests can cost money; no budget enforcement exists. Provider text is untrusted, must be reviewed, and is never executed as code.

1. Configure and migrate `AATM_DATABASE_URL` to Alembic head, create a project and pending task, and assign an agent from that project. Use the local API to set that agent's `provider` to `openai`, `model` to an actual model ID available to your account, and optionally `instructions`. The current dashboard cannot edit provider/model settings. Keep `OPENAI_API_KEY` in the local process environment, never in an agent record or argument.
2. Run from `backend`:

   ```sh
   python -m app.task_worker run --task-id TASK_ID --confirm-billable --confirm-data-transfer
   ```

   Replace `TASK_ID` with an integer. The task must be pending, have all direct dependencies completed, and be assigned to a matching OpenAI agent. Both confirmations are mandatory. A project lock and database partial unique index allow only one unresolved run per task. The worker snapshots task/agent content at claim time; later edits, reassignment, cancellation or completion can occur independently, so the output may not reflect current state. The read-only ready-task list is only a planning snapshot and may still include a task with an unresolved run.
3. On a successful complete provider response, the draft is printed to stdout after recording `succeeded`; it is **not saved in the database**, and stdout/terminal scrollback or redirection may retain it. Terminal control/format characters are stripped and long output truncated, so the displayed text can differ. Input/output token counts are recorded when available, but cost is not calculated. A successful response does not complete the task; a human must review it and explicitly complete the task separately. A process crash, output failure or database failure can lose the draft even if the remote call succeeded. The database stores run ID, task and agent references, model, timestamps, status and optional token counts, not input, output or API keys. The unauthenticated local API exposes metadata at `GET /api/tasks/{task_id}/runs`; refresh the dashboard to see it.

A timeout, provider error or client initialization failure is recorded as `uncertain`, since the remote outcome or charge may be unknown. A process crash can leave `running`. Both states block further runs for that task; there is **no automatic retry or expiry**. Investigate the remote outcome and ensure the original worker has actually stopped before deliberately releasing the claim:

```sh
python -m app.task_worker resolve --run-id RUN_ID --confirm-worker-stopped
```

Resolution does not prove success or cancel a remote request. Resolving while a worker is still active can permit duplicate billable requests; do not do so. If the original worker later finishes after resolution, its result is suppressed. Database admins can bypass these controls; the system has no authentication or tamper-proof audit and must remain local. Task and agent deletion is restricted while *any* run history references them; there is currently no retention/purge UI or API. Preserve and back up history before administrative changes. Migration 0009 refuses downgrade if history exists; on SQLite multi-step downgrades can partially apply earlier DDL before a later guard fails, so back up and inspect migration state. No actual provider call was made during development; all provider tests are mocked and real credentials, platform compatibility and billing remain unverified.

## Opt-in one-shot batch scheduling

A local operator can process a bounded batch of **previously unattempted** assigned tasks from one **active** project, sequentially, using the same worker and safeguards described above:

```sh
python -m app.task_scheduler --project-id PROJECT_ID --max-tasks 3 --confirm-billable --confirm-data-transfer
```

Replace `PROJECT_ID` with an integer. The maximum is explicitly required and must be 1–20; it limits requests, **not monetary cost**. Both flags authorize transfer and potential billing for every task selected in this project, so review all eligible tasks and assigned agent instructions before invoking. Selection requires a pending task, completed direct prerequisites, same-project assignment, provider `openai`, nonblank model, an active project, and **no prior run history of any status**. Tasks are selected by ID up to the limit, then rechecked and claimed one by one under the project lock; competing scheduler/worker claims cannot cause a batch retry of an already-attempted task. A changed task or an error stops the batch rather than skipping it. A provider error can be billed even when uncertain, so inspect before any further operation. A subsequent explicit batch may process other untouched tasks but never retries a task with history, even after resolution. Use the separately confirmed single-task worker for an intentional repeat.

Outputs are printed sequentially to stdout; task IDs and status messages go to stderr. Do not execute them automatically and protect terminal scrollback and redirects. Task and agent records may change between selection and the per-task claim; data are snapshotted only at claim. Results do not complete tasks; downstream dependencies remain blocked until manual completion. This is **not** a persistent daemon, parallel pool, comprehensive scheduler, global agent concurrency limit, budget manager, authenticated service or recovery mechanism. Multiple operators or processes can run different tasks simultaneously and no global cap on concurrent agents is enforced. Process failure can leave running or uncertain claims, requiring the manual investigation and resolution described above. No live OpenAI request was performed in development or CI.
