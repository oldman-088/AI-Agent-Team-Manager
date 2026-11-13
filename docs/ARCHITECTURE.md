# Architecture

## Current state

The checked-in local prototype uses Python's standard library, a SQLite database, and a static JavaScript UI. It manages agent labels and tasks only. It is unauthenticated, has no actual agents, providers, projects or execution, and is **not production-ready**. Existing data is not automatically migrated to any future database.

## Target architecture (proposed, not implemented)

React/TypeScript UI → local API (FastAPI) → application services → repositories and explicit provider/worker/browser/GitHub ports. PostgreSQL is the authoritative operational store; Alembic versions the schema. The API and scheduler coordinate durable state transitions and audit events. Worker processes execute only explicitly authorized actions in isolated project workspaces, using scoped credentials and bounded concurrency (initially up to 20). Provider and browser implementations stay behind replaceable adapters. Events may initially be delivered by SSE; choose a queue only once durable dispatch requirements are specified. Progress Markdown is a derived report, never authoritative runtime state.

## Boundaries and risks

The browser UI is untrusted input; local does not mean authenticated. Model output, repository content, web pages, and tool results are untrusted. Validate every tool request and do not treat model instructions as authorization. Separate credentials and browser profiles per principal/project, minimize access, never put secrets in logs or memory. GitHub writes and destructive actions need policy gates; no automatic protected-branch merge or production deployment. Sandboxing must be selected and tested rather than inferred from a Python process boundary. Local API must bind loopback by default and have authentication and DNS-rebinding/CSRF defenses before managing privileged tools.

## Data and execution design to validate

Project-scoped entities and relationships, dependency cycle detection, atomic task claims, idempotency keys for side effects, lease/heartbeat semantics, bounded retry policies and process liveness checks must be specified and tested before executing agents. Workers must not report running without an actual active execution. Database transactions, user authorization and isolation are required before any multi-user or remote deployment. Operational events must not contain secret-bearing payloads.

## Implementation approach

Preserve the prototype until a tested replacement and explicit data migration exist. Phase 1 introduces backend/frontend scaffolds, configuration, health endpoints, PostgreSQL connectivity and migrations; each later subsystem requires its own acceptance tests and threat review. Current repository paths intentionally remain small rather than creating empty modules that imply functionality.
