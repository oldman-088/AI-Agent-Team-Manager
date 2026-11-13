# Technical decisions

## 2026-11-13: Phase 0 baseline

- Keep the existing SQLite/static prototype intact and explicitly unsupported for production. No data migration is claimed. Replace it incrementally, with an explicit migration decision before removal.
- Target FastAPI/Pydantic, SQLAlchemy/Alembic and PostgreSQL, and React/TypeScript/Vite for Phase 1 as requested; exact versions and licenses remain to be reviewed. Do not add Redis without a demonstrated need.
- Prefer Playwright for future browser control and E2E coverage; no browser dependency or installation is yet present.
- Prefer official provider SDKs behind AATM-owned interfaces initially. Framework and provider selections remain unvalidated; see research.
- No application license is selected: the repository owner has not supplied one. Do not invent a license grant. Verify third-party obligations before distributing dependencies.
- Work on the session's existing branch; platform constraints prohibit creating or switching branches. A PR can be prepared from this branch, subject to review and branch rules.
