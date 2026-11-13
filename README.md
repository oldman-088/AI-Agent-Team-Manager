# AI Agent Team Manager

A small, local-first foundation for organizing agents and tasks. Create agents with roles, create and assign tasks, change task status, and remove records. Data persists in SQLite. This is a task tracker: it does **not** run AI agents, call model providers, authenticate users, or coordinate autonomous execution. The repository contained no product specification beyond its name, so these capabilities are an initial interpretation, not a claim that the intended project is complete.

## Run

Requires Python 3.9 or newer; no third-party dependencies.

```sh
python -m team_manager.app
# Open http://127.0.0.1:8000
```

Options: `--host` (default `127.0.0.1`), `--port` (default `8000`), and `--db` (default `team_manager.sqlite3` in the current working directory). The database is initialized on startup; back it up before replacing or removing it. No environment variables or external credentials are required.

**Security:** This is a single-user local development application, not a production service. It has no authentication, authorization, TLS, or multi-user isolation. Do not expose it to untrusted networks, or use it for sensitive data. Write requests require JSON and reject cross-origin browser requests, but these checks are not a substitute for authentication. Binding to a public interface is explicitly at your own risk. Production deployment requires authentication, access control, TLS, an appropriate server and security review.

## Architecture and API

`team_manager/app.py` serves the static UI and JSON API using Python's standard library. SQLite stores `agents` (name, role, creation time) and `tasks` (title, description, status, optional agent reference, creation time). Deleting an agent unassigns its tasks. Schema creation is idempotent; there is no versioned migration framework yet.

- `GET /api/agents`, `POST /api/agents` (`name`, `role`), `DELETE /api/agents/{id}`
- `GET /api/tasks`, `POST /api/tasks` (`title`, optional `description`, optional `agent_id`), `PATCH /api/tasks/{id}` (`status` and/or `agent_id`), `DELETE /api/tasks/{id}`
- Status values: `todo`, `in_progress`, `done`; use `null` to unassign an agent. Mutations require `Content-Type: application/json`. Errors return JSON with an `error` field.

## Tests

```sh
python -m unittest discover -s tests -v
python -m compileall -q team_manager tests
```

## Limitations and next steps

No agent execution, LLM integration, workflow engine, integrations, authentication, collaboration, task editing beyond status and assignment, versioned migrations, or production deployment configuration exists. Product requirements and acceptance criteria are needed before those capabilities can be designed and verified. See `progress/WORKFLOW_REPORT.md` for the current checkpoint.

## Project direction

The supplied AATM master specification defines the intended platform; this prototype implements only a small local task tracker, not that platform. See [architecture](docs/ARCHITECTURE.md), [research](docs/RESEARCH.md), [decisions](docs/TECHNICAL_DECISIONS.md), and [roadmap](docs/ROADMAP.md). The new Phase 1 foundations are separate from the prototype: see [backend](backend/README.md) and [frontend](frontend/README.md). PostgreSQL migrations require a configured database. The new frontend can create and list basic project and agent-configuration records; provider and agent integrations do not yet exist.
