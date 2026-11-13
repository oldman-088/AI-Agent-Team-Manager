# Third-party dependencies

The legacy prototype has no third-party application runtime dependencies. The new backend declares FastAPI, Uvicorn, SQLAlchemy, Alembic and psycopg; its optional test dependencies are pytest and httpx. The new frontend declares React, React DOM, Vite, TypeScript and Vitest; exact npm dependency versions are in frontend/package-lock.json. Python dependency ranges are not yet locked and require a reproducibility/security review. CI uses GitHub-hosted actions: `actions/checkout`, `actions/setup-python`, and GitHub CodeQL actions. Workflow major tags are convenient but mutable; pin to verified commit SHAs before treating CI as hardened. Hosted runner images and tools are external dependencies too.

Playwright remains proposed and is not installed. Before adoption, record exact version, license, provenance, transitive dependencies, maintenance and vulnerability review. See [research](RESEARCH.md) and [license compliance](LICENSE_COMPLIANCE.md).

The backend now declares `openai>=2,<3` (official SDK; repository reports Apache-2.0). Exact Python versions and transitive licenses are not locked or fully audited. The adapter was tested with mocks and the SDK's mock HTTP transport, not a live provider. See [provider research](RESEARCH.md).
