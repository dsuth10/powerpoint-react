## AI PowerPoint Generator – Runbook (Windows + Docker Compose)

This runbook documents how to start, access, and troubleshoot the app locally using Docker Compose on Windows PowerShell. It reflects the current working configuration (frontend on port 5173 with proxy to backend on 8000).

### What’s in this guide
- How to start the stack
- How to verify health and access the UI
- Ports, URLs, and service layout
- Troubleshooting common issues (port mismatch, CORS, WebSockets)
- Useful commands (PowerShell-safe)
- Optional: run services without Docker

---

## 1) Prerequisites
- Docker Desktop (with Docker Compose v2)
- Windows PowerShell
- Ports 5173 (frontend) and 8000 (backend) available

Optional for non-Docker runs:
- Node.js 18.19.0 (see `frontend/Dockerfile` and `planning_documents/versions.md`)
- Python 3.12 (see `backend/requirements*.txt`)

Key files:
- `docker-compose.yml` (dev compose)
- `frontend/vite.config.ts` (Vite dev server + proxy)
- `backend/app/main.py` (FastAPI app + WebSocket mount)

---

## 2) Start the stack

Run from the project root in PowerShell:

```powershell
docker compose up -d --build
```

Check containers and port mappings:

```powershell
docker compose ps
```

Expected (abbreviated):
- `backend`: 0.0.0.0:8000->8000/tcp
- `frontend`: 0.0.0.0:5173->5173/tcp

Stop the stack:

```powershell
docker compose down
```

---

## 3) Verify health and access the app

Backend health:

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

Expected JSON:

```json
{"status":"ok","version":"1.0.0","git_sha":"mock-sha"}
```

Frontend UI:

- Open `http://localhost:5173` in your browser.

If you see HMR or Vite client logs in the console, the dev server is running.

---

## 4) Service layout, ports, and proxies

- Frontend dev server (Vite): `http://localhost:5173`
  - Configured in `frontend/vite.config.ts` with `server.port = 5173` and `strictPort = true`.
  - Proxies:
    - `/api` → `http://localhost:8000` (backend API)
    - `/ws` → `http://localhost:8000` (WebSocket)

- Backend API (FastAPI): `http://localhost:8000`
  - OpenAPI served at `/api/v1/openapi.json`
  - Health: `/api/v1/health`
  - WebSocket: mounted at `/ws` (Socket.IO path `socket.io`)

---

## 5) Common issues and fixes

- Port mismatch (frontend unreachable):
  - Symptom: browser or tools show `ERR_CONNECTION_REFUSED` on `http://localhost:5174`.
  - Fix: frontend is served on 5173. Use `http://localhost:5173` and ensure `docker-compose.yml` maps `5173:5173`.

- API requests blocked by CORS:
  - Use the built-in Vite proxy (already configured) so the frontend calls `/api/...` and `/ws` instead of direct `http://localhost:8000`.

- WebSocket not connecting:
  - Ensure the proxy for `/ws` exists in `frontend/vite.config.ts` and the backend mounts the Socket.IO app at `/ws` (`backend/app/main.py`).
  - Socket.IO path is `socket.io` under `/ws`, e.g., `/ws/socket.io`.

- Rate limit 429s during testing:
  - Default limit: 100 requests per 15 minutes (see `backend/app/core/rate_limit.py`).

- API key requirement (disabled by default):
  - If `REQUIRE_API_KEY=true` and `API_KEYS` set in backend env, include header `X-API-Key: <your_key>` for non-auth POST routes.

- Playwright headless UI snapshot shows refusal but network OK:
  - This can be a transient headless rendering race. Verify with browser and confirm network 200s.

---

## 6) Useful PowerShell commands

Logs (frontend or backend):

```powershell
docker compose logs --tail=200 frontend
docker compose logs --tail=200 backend
```

Quick health checks:

```powershell
Invoke-WebRequest -Uri http://localhost:5173 -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

Rebuild and restart:

```powershell
docker compose down; docker compose up -d --build; docker compose ps
```

---

## 7) Running without Docker (optional)

Backend (FastAPI):

```powershell
cd backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend (Vite):

```powershell
cd frontend
npm ci
npm run dev
```

Ensure `frontend/vite.config.ts` proxy targets `http://localhost:8000` for `/api` and `/ws`.

---

## 8) API quick tests

Generate outline (fallback works without external LLM keys):

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/chat/generate -Method POST -ContentType 'application/json' -Body '{"prompt":"Demo","slide_count":3}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

Build slides (mock job response):

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/slides/build -Method POST -ContentType 'application/json' -Body '[{"title":"Title","bullets":["Bullet"]}]' -UseBasicParsing | Select-Object -ExpandProperty Content
```

Download (will 404 unless a file exists at the configured temp dir):

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/slides/download?jobId=<uuid>" -UseBasicParsing
```

---

## 9) Notes for contributors

- If you change ports or proxy settings, update both `docker-compose.yml` and `frontend/vite.config.ts`.
- For API changes, regenerate the frontend client with:

```powershell
cd frontend
npm run openapi:gen
```

- Relevant source references:
  - Frontend proxy/ports: `frontend/vite.config.ts`
  - Compose services: `docker-compose.yml`
  - Backend routes: `backend/app/api/*`
  - WebSocket mount: `backend/app/main.py` and `backend/app/socketio_app.py`

---

If anything here doesn’t match your environment, please capture the difference (ports, logs, errors) and adjust the steps accordingly.


