# Frontend foundation

Requires Node.js 22.12+ (or a newer version supported by Vitest) and npm. Run `npm ci`, then `npm run dev`. The Vite development server listens on loopback and proxies `/health` to the local backend on port 8001. Start the backend separately; see `backend/README.md`. Run `npm test`, `npm run typecheck`, and `npm run build`. The dashboard checks database connectivity and is not an agent management UI yet. No authentication or production deployment is provided. The Vite proxy is for local development, not production.

The dashboard lists and creates basic project records when the backend database is migrated and reachable. Edit and delete operations are API-only. A limited Chromium end-to-end test runs in GitHub Actions.

Agent configuration records can be created and listed, optionally associated with a project. Editing and deletion are API-only; these records do not execute agents or validate provider/model configuration.

The dashboard creates and lists planning tasks linked to projects; task editing, cancellation and deletion are API-only. Lists and project selectors currently show only the first 100 results; pagination controls are not implemented.

The current dashboard supports English, Arabic and Persian via its language selector. It applies document-level `lang` and `dir`, logical spacing, and bidirectional isolation for user-entered text; changing language is temporary and resets on reload. Automated DOM tests cover language switching, translated errors and direction, and a Chromium E2E smoke test checks locale changes, inherited RTL direction and basic keyboard focus. Full visual, keyboard, screen-reader and product-wide RTL validation remain outstanding.

## Browser end-to-end test

Install backend test dependencies in an active Python environment, run `npm ci`, and install Chromium with `npx playwright install chromium` (Linux may require Playwright's documented system dependencies). Then run `npm run test:e2e` from `frontend/`. The test starts a dedicated backend on 127.0.0.1:8018 and Vite on 127.0.0.1:5178; it creates and migrates a disposable SQLite database in a system temporary directory, ignoring `AATM_DATABASE_URL`, and refuses to reuse existing servers. Never substitute a real user database for the test database. On forced process termination the operating system temporary directory may require cleanup. CI executes the browser test on Ubuntu; this does not establish Windows/browser-profile compatibility or full accessibility compliance. The Vite server-only `AATM_BACKEND_PROXY` variable changes the development proxy target and defaults to `http://127.0.0.1:8001`; do not point it to untrusted hosts or expose the dev server.

A pending planning task may be marked completed manually from the dashboard if its direct dependencies are completed. This is the user's assertion, not evidence of agent execution or review. Dependency editing and readiness details remain API-only.

Recent task activity is shown as metadata with database-provided timestamps. It is not a tamper-proof or authenticated security audit, and the UI currently loads only the first 100 events.

Select a loaded task to inspect its dependency IDs and readiness snapshot, and add or remove prerequisites from the same project's loaded tasks. Choices are limited to the first 100 tasks loaded in the dashboard; dependencies outside that page are shown by ID. Readiness can become stale, and the server rechecks it on manual completion. The API remains authoritative for cycles, status and concurrent edits.

A selected pending task can be manually assigned to an agent configuration from the same project. The first 100 loaded agents are available; an existing assignment outside that page is identified by ID. Assignment is planning only and starts nothing. Assignments can be removed from completed or cancelled tasks without deleting the task; adding or changing an agent still requires a pending task. Refresh and reselect the task to observe changes made elsewhere.
