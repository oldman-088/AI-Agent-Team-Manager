# Roadmap and acceptance

The master specification supplied by the user is the authoritative requirements source. Overall completion is unknown; no weighted estimate is credible until the full scope is decomposed into verifiable tasks.

- Phase 0 — **In Progress**: research, architectural baseline, CI, issue/milestone planning. CI must actually run before verification. Research is preliminary, not a full security or license audit.
- Phase 1 — **In Progress**: FastAPI, React/TypeScript, PostgreSQL, configuration, health and Alembic. Foundation implemented; PostgreSQL CI validation and further work pending. Acceptance: documented startup, migrations and automated integration tests against PostgreSQL.
- Phase 2 — **In Progress**: initial configuration registry implemented; lifecycle and heartbeat not implemented. Acceptance: states reflect real processes; stale-heartbeat recovery tests.
- Phase 3 — **In Progress**: narrow OpenAI SDK text adapter implemented with mocked tests; credential management, streaming and live integration verification remain outstanding.
- Phase 4 — **In Progress**: project-scoped planning tasks and dependency graph API; dependency-based scheduling, durable coordination and safe execution remain unimplemented.
- Phase 5 — **Not Started**: isolated Playwright sessions and persistent profiles.
- Phase 6 — **Not Started**: projects and authorized GitHub integration.
- Phase 7 — **Not Started**: scoped shared memory.
- Phase 8 — **Not Started**: QA and recovery.
- Phase 9 — **Not Started**: monitoring, approvals and security.
- Phase 10 — **In Progress**: current dashboard translated into English/Arabic/Persian with document direction and DOM tests; full UI and real-browser RTL and accessibility validation remain outstanding.
- Phase 11 — **Not Started**: end-to-end, security, performance, Windows and Ubuntu validation, release.

See the master specification for complete acceptance criteria. The existing prototype is not a substitute for these phases.
