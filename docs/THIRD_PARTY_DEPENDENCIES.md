# Third-party dependencies

Current prototype has no third-party application runtime dependencies. CI uses GitHub-hosted actions: `actions/checkout`, `actions/setup-python`, and GitHub CodeQL actions. Workflow major tags are convenient but mutable; pin to verified commit SHAs before treating CI as hardened. Hosted runner images and tools are external dependencies too.

Proposed, not yet installed: FastAPI, Pydantic, SQLAlchemy, Alembic, a PostgreSQL driver, React, TypeScript, Vite and Playwright. Before adoption, record exact version, license, provenance, transitive dependencies, maintenance and vulnerability review. See [research](RESEARCH.md) and [license compliance](LICENSE_COMPLIANCE.md).
