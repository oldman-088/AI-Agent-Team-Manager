# Frontend foundation

Requires Node.js 22.12+ (or a newer version supported by Vitest) and npm. Run `npm ci`, then `npm run dev`. The Vite development server listens on loopback and proxies `/health` to the local backend on port 8001. Start the backend separately; see `backend/README.md`. Run `npm test`, `npm run typecheck`, and `npm run build`. The dashboard checks database connectivity and is not an agent management UI yet. No authentication or production deployment is provided. The Vite proxy is for local development, not production.

The dashboard lists and creates basic project records when the backend database is migrated and reachable. Edit and delete operations are API-only. A browser end-to-end test has not yet been performed.

Agent configuration records can be created and listed, optionally associated with a project. Editing and deletion are API-only; these records do not execute agents or validate provider/model configuration.

The dashboard creates and lists planning tasks linked to projects; task editing, cancellation and deletion are API-only. Lists and project selectors currently show only the first 100 results; pagination controls are not implemented.
