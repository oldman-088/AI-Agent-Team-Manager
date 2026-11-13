# Backend foundation

Python 3.11+. From this directory create a virtual environment, then `pip install -e ".[test]"`. Set `AATM_DATABASE_URL` to a dedicated PostgreSQL database URL using SQLAlchemy's `postgresql+psycopg://` scheme. Use a local secret store or environment variables for credentials; never commit the URL if it contains credentials. Run `alembic upgrade head`, then `uvicorn app.main:app --host 127.0.0.1 --port 8001`. See `/docs`, `/health/live` and `/health/ready`. Readiness checks connectivity, not migration version. Missing configuration or an unreachable database returns 503 without exposing details.

Test with `pytest`; to exercise PostgreSQL migration upgrade/downgrade set `AATM_TEST_DATABASE_URL` to an **empty disposable database**. The test drops its `projects` table; never point it at valuable data. Without that variable SQLite is only a local smoke test. The initial schema and health probes do not implement project management or migrate the old SQLite prototype. No authentication is implemented: use loopback only and do not expose this service publicly.

## Project API

After migrations: `GET /api/projects` lists up to 100 records (`limit` 1–100, `offset` 0–1000000); `POST /api/projects` accepts `name`, optional `description`, and optional `status`. `GET`, `PATCH`, and `DELETE /api/projects/{id}` retrieve, update, and delete a record. Status values are `planned`, `active`, `paused`, `completed`, and `archived`. Deletes are permanent. The API currently stores only name, description, and status; it does not connect repositories, run agents, isolate projects, or implement full project management. Legacy prototype data is separate.

A localhost Host allowlist and origin/content-type checks reduce browser-based DNS rebinding and cross-origin write risks. They do not authenticate local users or protect against malicious local processes. Do not expose this API publicly, use it with sensitive data, or treat it as production-ready. The Vite proxy must be accessed via localhost or 127.0.0.1 for these checks.
