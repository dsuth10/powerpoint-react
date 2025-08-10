# AI-PowerPoint-Generator Monorepo

![CI](https://github.com/dsuth10/powerpoint-react/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/dsuth10/powerpoint-react/actions/workflows/codeql.yml/badge.svg)

This repository contains both the frontend (React + Vite + TypeScript) and backend (FastAPI) for the AI-PowerPoint-Generator project.

## What’s new

- Strict Pydantic v2 base model with camelCase JSON aliasing (`backend/app/models/base.py`)
- PRD-aligned domain models:
  - `ChatRequest` (prompt, slideCount, model, …)
  - `ChatResponse` (slides, optional sessionId)
  - `SlidePlan` (title, bullets, image, notes)
  - `ImageMeta` (url with validation, altText, provider)
  - `PPTXJob` (UUID jobId, status enum, resultUrl, errorMessage)
  - `ErrorResponse` (errorCode, message, details)
- Chat API updated to return `ChatResponse` from `POST /api/v1/chat/generate`
- CI/CD hardening: concurrency, npm/pip caching, coverage ≥ 90% gates, artifact uploads, k6 smoke, Docker build + Trivy scan (frontend & backend), SBOMs, CodeQL, deploy/release workflows
- Make targets and PowerShell scripts for smoke/verify
- Backend system improvements:
  - Rate limiting applied to public POST routes via `Depends(rate_limit_dependency)`; OpenAPI now documents 429 responses where applicable
  - Auth refresh documents 401; slides builder documents 422 for validation errors
  - `/metrics` endpoint exposed with `text/plain` content type and included in OpenAPI
  - OpenAPI forced to 3.0.3 for better tooling compatibility
  - LLM calls short-circuit offline (no API key) to keep local tests fast and deterministic
  - Download endpoint added: `GET /api/v1/slides/download?jobId=<uuid>` serves generated PPTX with correct headers
  - Real-time updates via Socket.IO mounted at `/ws` with events `slide:progress`, `slide:completed`, and `resume` (optional auth via JWT or `sessionId`)

## Project Structure

- `frontend/` – React 18 + Vite + TypeScript app
- `backend/` – FastAPI app (entry: `backend/app/main.py`)

## Getting Started

### Prerequisites
- Node.js 18.19.0 (see `.nvmrc`)
- Python 3.12.0 (see `backend/.python-version`)
- Docker Desktop (for dev workflow)

### Install dependencies

```sh
cd frontend && npm install
cd ../backend && pip install -r requirements.txt -r requirements-dev.txt
```

### Development (Docker Desktop)

PowerShell (Windows):
```powershell
make up
./scripts/smoke.ps1
```

Bash (macOS/Linux):
```sh
make up && sleep 5
curl -f http://localhost:8000/api/v1/health && curl -f http://localhost:5173 || true
```

### Quality Checks

- Lint & test frontend (coverage ≥ 90% enforced in CI):
  ```sh
  npm run quality:frontend
  ```
- Lint & test backend (coverage ≥ 90% enforced in CI via pytest.ini):
  ```sh
  npm run quality:backend
  ```
- All quality checks:
  ```sh
  npm run quality
  ```

Makefile shortcuts (run from repo root):

```sh
make up        # build & start dev stack
make down      # stop stack
make logs      # tail container logs
make quality   # backend lint+tests locally
```

### Backend Testing (local)

Run backend tests with Schemathesis explicitly enabled (we disable auto-loaded plugins for stability):

PowerShell (Windows):

```powershell
cd backend
$env:PYTHONPATH=(Get-Location).Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -q -p schemathesis
```

Bash:

```sh
cd backend
PYTHONPATH=$(pwd) PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p schemathesis
```

Notes:
- If you omit `-p schemathesis` while disabling auto plugins, contract tests will fail due to a missing `case` fixture.
- Tests do not call external LLMs when `OPENROUTER_API_KEY` is unset; the API returns a local fallback for speed.

### Environment Variables
- Frontend expects `VITE_BACKEND_URL` and `VITE_WS_URL`. In Docker dev, these are provided by compose. For local overrides, create `frontend/.env.local` with:

  ```env
  VITE_BACKEND_URL=http://localhost:8000
  VITE_WS_URL=ws://localhost:8000/ws
  ```

- Backend keys (for live API calls). For simplest usage, just set your keys and run; no login/JWT required:

  ```env
  # .env (repo root) or environment variables
  OPENROUTER_API_KEY=sk-or-...
  STABILITY_API_KEY=sk-stability-...
  ```

  Notes:
  - If keys are not set, the backend returns local fallbacks where applicable so you can still develop and run tests.
  - When deploying publicly, enable authentication and tighten CORS/Rate Limits.

# Stage 1 Foundation Complete

- Both frontend and backend are fully Dockerized. All development, testing, and quality checks must be run in Docker for consistency and cross-platform reliability.
- All lint, format, type check, and test commands pass in Docker for both frontend and backend.
- CI/CD is set up with GitHub Actions (see `.github/workflows/ci.yml`) for lint, type-check, tests with coverage thresholds, artifacts, Docker build/scan, SBOMs, k6 smoke.
- Node.js 18.19.0 and Python 3.12.0 are required (enforced in Docker and CI).
- All dependencies are pinned and must match planning_documents/versions.md.
- Backend: use Makefile targets for lint/test, or run ruff, black, mypy, pytest directly in Docker.
- Frontend: use npm scripts (lint, test, dev, build) in Docker only.
- If you switch between running npm on Windows and in Docker, always delete node_modules and reinstall in Docker to avoid native module issues.
- See planning_documents/stage-1-foundation.md for full setup history and compliance checklist.
- To run all quality checks in Docker:
  - Backend:
    ```sh
    docker compose run --rm backend ruff . && \
    docker compose run --rm backend black --check . && \
    docker compose run --rm backend mypy . && \
    docker compose run --rm backend pytest --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml
    ```
  - Frontend:
    ```sh
    docker compose run --rm frontend npm run lint && \
    docker compose run --rm frontend npm run test -- --run --coverage
    ```
- All contributors must read the planning documents before making changes.

## 🚨 Mandatory Docker Workflow for Frontend

To guarantee a consistent, working, and cross-platform development and CI environment for the frontend, **all commands (test, build, lint, etc.) must be run inside the provided Docker container**.

### Why?
- Ensures all contributors and CI/CD use the same Node, npm, and dependency versions
- Prevents platform-specific errors (especially on Windows)
- Guarantees reproducible builds and test results

### How to use
1. Build the Docker image:
   ```sh
   docker build -t ppt-frontend-dev ./frontend
   ```
2. Run commands in the container, e.g.:
   ```sh
   docker run --rm ppt-frontend-dev
   ```
   or for interactive development:
   ```sh
   docker run --rm -it -v $(pwd)/frontend:/app -w /app ppt-frontend-dev sh
   ```

> **Note:** Local Node.js/npm installations on Windows or Mac **must not** be used for these tasks. All documentation and onboarding must reference this workflow. See `.cursor/rules/docker-dev-environment.mdc` for the full policy.

## API quick reference

- `POST /api/v1/chat/generate` → `ChatResponse`
  - Request body (`ChatRequest`): `{ prompt: string, slideCount: number (1–20), model: string, language?: string, context?: string }`
  - Response: `{ slides: SlidePlan[], sessionId?: string }`
  - `SlidePlan`: `{ title: string, bullets: string[], image?: ImageMeta, notes?: string }`
  - `ImageMeta`: `{ url: string, altText: string, provider: string }`
  - Possible errors: `429 Too Many Requests`
- `POST /api/v1/auth/login` → `TokenPair`
  - Possible errors: `429 Too Many Requests`
- `POST /api/v1/auth/refresh` → `TokenPair`
  - Possible errors: `401 Unauthorized`, `429 Too Many Requests`
- `POST /api/v1/slides/build` → `PPTXJob`
  - Possible errors: `422 Validation Error`, `429 Too Many Requests`
- `GET /api/v1/slides/download?jobId=<uuid>` → PPTX file download
  - Content-Type: `application/vnd.openxmlformats-officedocument.presentationml.presentation`
  - Filename: `presentation-<jobId>.pptx`
  - Possible errors: `404 Not Found`
- `GET /metrics` → Prometheus text exposition format (`text/plain`)

### WebSocket (Socket.IO)

- Base path (HTTP): `/ws` (Socket.IO path: `/ws/socket.io`)
- Example client URL (dev): `http://localhost:8000` with `socketio_path="/ws/socket.io"`
- Events emitted by server:
  - `slide:progress` – payload with progress details
  - `slide:completed` – payload with result metadata
  - `resume` (client → server) – request replay of missed events with `{ sessionId: string, fromIndex?: number }`
- Authentication (optional in dev):
  - JWT via `Authorization: Bearer <access-token>`
  - or `sessionId` UUID via connection `auth` payload or query string

## Scripts

- `scripts/smoke.ps1` – bring up the stack and smoke-check FE/BE
- `scripts/verify.ps1` – repo and versions sanity checks
