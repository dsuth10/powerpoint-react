# Frontend (React 18 + TypeScript + Vite)

This is the React frontend for the AI‑PowerPoint‑Generator monorepo. It runs in Docker for a consistent dev experience across platforms (especially Windows).

## Tech stack (current)
- React 18.2 (TypeScript)
- Vite 5 + `@vitejs/plugin-react`
- TanStack React Router v1 (manual route composition; Vite plugin removed)
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

## Troubleshooting
- If the frontend 500s on startup or dependencies seem stale:
  - Run `docker compose down -v` and `docker compose up -d`
  - Check logs: `docker compose logs frontend --tail=200`
  - Ensure Docker Desktop is running

## Conventions
- Absolute import alias `@` maps to `src/` (see `vite.config.ts`).
- Keep dependency versions aligned with `planning_documents/versions.md`.
