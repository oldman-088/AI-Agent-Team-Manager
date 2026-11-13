# Frontend foundation

Requires Node.js 22.12+ (or a newer version supported by Vitest) and npm. Run `npm ci`, then `npm run dev`. The Vite development server listens on loopback and proxies `/health` to the local backend on port 8001. Start the backend separately; see `backend/README.md`. Run `npm test`, `npm run typecheck`, and `npm run build`. The dashboard checks database connectivity and is not an agent management UI yet. No authentication or production deployment is provided. The Vite proxy is for local development, not production.
