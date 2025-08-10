# Frontend (React 18 + TypeScript + Vite)

This is the React frontend for the AI‑PowerPoint‑Generator monorepo. It runs in Docker for a consistent dev experience across platforms (especially Windows).

## Tech stack (current)
- React 18.2 (TypeScript)
- Vite 5 + `@vitejs/plugin-react`
- TanStack React Router v1 (manual route composition; Vite plugin removed)
- TanStack React Query v5 (data fetching & caching)
- Tailwind CSS 3.4 + `tailwindcss-animate`
- ESLint (flat config), Prettier, Vitest (configured in repo)

Notes:
- We are NOT using `@tanstack/router-vite-plugin` right now. Routes are composed manually in `src/router.ts` from files in `src/routes/*`.
- The dev server binds to `0.0.0.0` for Docker access.

## Prerequisites
- Docker Desktop running

## Run (Docker)
Use PowerShell commands (Windows) as preferred.

```powershell
# From repo root
docker compose up -d

# Frontend URL
Start-Process http://localhost:5173

# API health (backend)
Start-Process http://localhost:8000/api/v1/health
```

The compose file uses a named volume `node_modules_frontend` to persist dependencies between restarts. On dependency changes, the container runs `npm install --legacy-peer-deps` before starting Vite.

To force a clean rebuild (helpful after dependency or compose changes):

```powershell
docker compose down -v
docker compose build --no-cache backend frontend
docker compose up -d
```

## Scripts (inside container)
```powershell
docker compose run --rm frontend npm run dev      # Vite dev server (runs by default in service)
docker compose run --rm frontend npm run build    # Type-check + build
docker compose run --rm frontend npm run lint     # ESLint
docker compose run --rm frontend npm run test -- --run  # Vitest
docker compose run --rm frontend npm run openapi:gen    # Generate TS client from OpenAPI
```

## Routing
- Entry: `src/router.ts`
- Routes live in `src/routes/*` using TanStack Router v1 classes, then are composed manually via `rootRoute.addChildren([...])`.
- Example paths:
  - `/` (home)
  - `/chat`, `/chat/:sessionId`
  - `/slides`, `/slides/:slideId`

## Styling
- Tailwind is configured in `tailwind.config.js`
- Animations via `tailwindcss-animate`

## Backend connectivity (dev)
- The home page calls `http://localhost:8000/api/v1/health` and shows the status inline.
- CORS is open in dev; restrict in production.
- API base URL for generated client is controlled by `VITE_API_BASE_URL` (e.g., `http://localhost:8000/api/v1`).

## OpenAPI → TypeScript client & hooks

This project generates a type-safe API client from the backend FastAPI OpenAPI schema using `@hey-api/openapi-ts` and wraps mutations with TanStack Query.

### One-time dependencies (already pinned in package.json)
- `@hey-api/openapi-ts`
- `@hey-api/client-fetch`
- `@tanstack/react-query`

### Generate client
1) Export the backend OpenAPI schema to a local file (stable for codegen):
```powershell
cd backend
$env:PYTHONPATH='.'; python scripts/export_openapi.py --out ..\frontend\src\lib\api\openapi.json
```
2) Generate the client in the frontend:
```powershell
cd frontend
npm run openapi:gen
```
This creates/updates files under `src/lib/api/` (`types.gen.ts`, `sdk.gen.ts`, `client.gen.ts`, etc.). Do not edit generated files manually.

### Configure base URL
- Recommended: set `VITE_API_BASE_URL` (e.g., `http://localhost:8000/api/v1`) in `frontend/.env.local`.
- If you use a helper module, import and provide it when calling SDK functions. If you removed the helper, pass config inline via `client.setConfig({ baseUrl: import.meta.env.VITE_API_BASE_URL })`.

### Using the hooks
- Custom hooks live in `src/hooks/api/index.ts` and wrap the generated SDK with TanStack Query v5:
  - `useGenerateChatMutation()` → POST `/chat/generate`
  - `useBuildSlidesMutation()` → POST `/slides/build`
  - These hooks set the client base URL from `VITE_API_BASE_URL`.

## Troubleshooting
- If the frontend 500s on startup or dependencies seem stale:
  - Run `docker compose down -v` and `docker compose up -d`
  - Check logs: `docker compose logs frontend --tail=200`
  - Ensure Docker Desktop is running

## Conventions
- Absolute import alias `@` maps to `src/` (see `vite.config.ts`).
- Keep dependency versions aligned with `planning_documents/versions.md`.
