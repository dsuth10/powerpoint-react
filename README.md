# AI-PowerPoint-Generator Monorepo

![CI](https://github.com/dsuth10/powerpoint-react/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/dsuth10/powerpoint-react/actions/workflows/codeql.yml/badge.svg)

This repository contains both the frontend (React + Vite + TypeScript) and backend (FastAPI) for the AI-PowerPoint-Generator project.

## What's new

- **🆕 Complete User Flow Implementation (August 2025)**: Full Chat → Slides navigation with session continuity, outline persistence, and seamless PowerPoint generation workflow
- **🆕 Stability AI API Integration Fixed (August 2025)**: Updated to use the current Stability AI v1 API with proper text-to-image generation, base64 image handling, and static file serving
- **✅ Working User Experience**: 
  - Seamless navigation between Chat and Slides sections with session persistence
  - Clear button labels ("Build PowerPoint" instead of confusing "Start Generation")
  - Real-time progress tracking during PowerPoint generation
  - Proper route parameters and state management across sections
  - Session-based outline persistence and retrieval
- Strict Pydantic v2 base model with camelCase JSON aliasing (`backend/app/models/base.py`)
- PRD-aligned domain models:
  - `ChatRequest` (prompt, slideCount, model, …)
  - `ChatResponse` (slides, optional sessionId)
  - `SlidePlan` (title, bullets, image, notes)
  - `ImageMeta` (url with validation, altText, provider)
  - `PPTXJob` (UUID jobId, status enum, resultUrl, errorMessage)
  - `ErrorResponse` (errorCode, message, details)
- Chat API returns `SlidePlan[]` from `POST /api/v1/chat/generate` (simplified shape for FE)
- LLM integration: OpenRouter `chat/completions` is the primary path with graceful fallback to legacy `/generate`; offline fallback remains for local dev. Optional attribution headers (`HTTP-Referer`, `X-Title`) are supported, and model IDs follow OpenRouter's current naming (e.g., `openai/gpt-4o-mini`).
- **🆕 Multi-Provider Image Generation System (August 2025)**: Complete refactor to support multiple AI image providers with automatic fallback and user selection
  - **DALL-E Integration**: Added OpenAI DALL-E 3 support as an alternative to Stability AI
  - **Provider Selection**: Users can choose between "Auto", "Stability AI", or "DALL-E" in the frontend
  - **Automatic Fallback**: System automatically falls back to available providers if preferred provider fails
  - **Factory Pattern**: Clean architecture with `ImageProvider` interface and provider registry
- **🆕 Image generation: Stability AI v1 API** with proper text-to-image generation using `/v1/generation/{engine_id}/text-to-image` endpoint, base64 image responses, and automatic static file serving
- Static hosting: `static/` ensured at startup and mounted at `/static`; public URLs built from `PUBLIC_BASE_URL`
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

## Recent Updates (August 2025)

### Complete User Flow Implementation ✅

**Problem Solved**: The application had broken navigation between Chat and Slides sections, confusing button labels, missing session continuity, and state isolation issues.

**Solution Implemented**:
1. **Seamless Chat → Slides Navigation**: Sidebar automatically passes current sessionId when navigating to Slides section
2. **Session Continuity**: Chat store maintains currentSessionId and session state across navigation
3. **Clear Button Labels**: Changed from "Start Generation" to "Build PowerPoint" for clarity
4. **Outline Persistence**: Slide outlines persist when switching between Chat and Slides sections
5. **Proper Route Parameters**: Implemented `/slides` and `/slides/:sessionId` routes with proper parameter handling
6. **State Management**: Fixed state isolation issues between sections

**Technical Changes**:
- `frontend/src/routes/pages/SlidesPage.tsx`: Complete implementation with outline retrieval from chat store
- `frontend/src/components/layout/Sidebar.tsx`: Automatic sessionId passing in navigation links
- `frontend/src/stores/chat-store.ts`: Session management and outline persistence
- `frontend/src/components/slides/GenerationControls.tsx`: Clear "Build PowerPoint" button labels
- `frontend/src/routes/slides/index.route.tsx`: Proper route configuration for session-based navigation

**Result**: Users can now seamlessly generate slide outlines in Chat, navigate to Slides section, and build PowerPoint files with real-time progress tracking. The complete user flow is fully functional.

### Stability AI API Integration Fixes

**Problem Solved**: The application was using outdated Stability AI API endpoints (`/images/generations` and `/v2beta/stable-image/generate/core`) that returned 405 Method Not Allowed errors.

**Solution Implemented**:
1. **Updated API Endpoint**: Now uses the current Stability AI v1 API: `POST /v1/generation/{engine_id}/text-to-image`
2. **Fixed Request Format**: Updated to use proper `text_prompts` array format instead of legacy `prompt` field
3. **Base64 Image Handling**: Implemented proper handling of base64-encoded image responses
4. **Static File Serving**: Images are automatically saved to `/app/static/images/` and served via `/static/images/`
5. **Field Name Compatibility**: Resolved camelCase vs snake_case field name issues for API compatibility

**Technical Changes**:
- `backend/app/models/stability.py`: Updated models for current API structure
- `backend/app/services/images.py`: Complete rewrite for v1 API integration
- `backend/app/core/config.py`: Added `STABILITY_ENGINE_ID` configuration
- Static file serving: Images are now properly accessible via HTTP

**Result**: The application now successfully generates AI-powered images for slides using the current Stability AI API, with proper error handling and fallbacks to placeholder images when needed.

### Multi-Provider Image Generation System ✅

**Problem Solved**: Users wanted the ability to choose between different AI image generation providers and have automatic fallback when one provider is unavailable or rate-limited.

**Solution Implemented**:
1. **DALL-E 3 Integration**: Added OpenAI DALL-E 3 as a second image generation provider alongside Stability AI
2. **Provider Selection UI**: Added dropdown in Slides section allowing users to choose "Auto", "Stability AI", or "DALL-E"
3. **Automatic Fallback Logic**: System automatically selects the best available provider based on configuration and availability
4. **Clean Architecture**: Implemented factory pattern with `ImageProvider` interface for easy addition of new providers
5. **Provider Registry**: Centralized provider management with automatic registration and status checking

**Technical Changes**:
- **Backend Architecture**:
  - `backend/app/services/image_providers/__init__.py`: Abstract `ImageProvider` interface and `ImageProviderFactory`
  - `backend/app/services/image_providers/stability.py`: Stability AI provider implementation
  - `backend/app/services/image_providers/dalle.py`: DALL-E provider implementation with OpenAI API integration
  - `backend/app/services/image_providers/registry.py`: Provider registration and selection logic
  - `backend/app/services/images.py`: Refactored to use provider factory pattern
  - `backend/app/core/config.py`: Added DALL-E configuration (`OPENAI_API_KEY`, `OPENAI_DALLE_MODEL`, etc.)
  - `backend/app/api/slides.py`: Added `/slides/providers` endpoint for provider status

- **Frontend Integration**:
  - `frontend/src/components/slides/GenerationControls.tsx`: Added provider selection dropdown
  - `frontend/src/stores/slide-generation-store.ts`: Added `imageProvider` state management
  - Provider selection persists during PowerPoint generation

**Configuration**:
- **DALL-E Setup**: Add `OPENAI_API_KEY` to `backend/.env` file
- **Provider Priority**: Configurable via `DEFAULT_IMAGE_PROVIDER` and `IMAGE_PROVIDER_FALLBACK_ORDER` in backend config
- **API Endpoints**: 
  - `GET /api/v1/slides/providers` - Returns available providers and their status
  - `POST /api/v1/slides/generate` - Accepts optional `provider` parameter

**Result**: Users now have full control over image generation with multiple provider options, automatic fallback for reliability, and a clean interface for selecting their preferred AI image generation service.

## Project Structure

- `frontend/` – React 18 + Vite + TypeScript app
- `backend/` – FastAPI app (entry: `backend/app/main.py`)

## Quick Start

**For Windows Users (Recommended):**
```powershell
# Start backend in Docker
docker-compose up backend -d

# Start frontend locally
cd frontend
npm run dev
```

**For macOS/Linux Users:**
```bash
# Start backend in Docker
docker-compose up backend -d

# Start frontend locally
cd frontend && npm run dev
```

Then open http://localhost:5173 in your browser.

## 🚀 User Flow Guide

The application now provides a complete, seamless user experience:

### **Recommended User Flow**
1. **Start in Chat**: Navigate to Chat section and enter a prompt (e.g., "Create a 5-slide presentation about renewable energy")
2. **Review Outline**: Generated slides appear as preview cards with titles and bullet points
3. **Refine if Needed**: Ask follow-up questions to improve the outline
4. **Switch to Slides**: Click "Slides" in the sidebar to see the complete outline
5. **Generate PPTX**: Click "Build PowerPoint" button to start generation
6. **Monitor Progress**: Watch real-time progress updates during generation
7. **Download**: Click "Download PPTX" when generation is complete

### **Key Features**
- ✅ **Session Continuity**: Your chat session and slide outlines persist when switching between sections
- ✅ **Clear Navigation**: Sidebar automatically includes your current session when navigating to Slides
- ✅ **Real-time Progress**: WebSocket connection provides live updates during PowerPoint generation
- ✅ **Multiple Sessions**: Create and manage multiple chat sessions with different slide outlines
- ✅ **Error Recovery**: Retry buttons and clear error messages for failed operations
- ✅ **Proxy Configuration**: Vite dev server properly proxies API and WebSocket calls to backend

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

### Development Options

#### Option 1: Docker Compose (Recommended)

PowerShell (Windows):
```powershell
docker-compose up backend -d
cd frontend
npm run dev
```

Bash (macOS/Linux):
```sh
docker-compose up backend -d
cd frontend && npm run dev
```

#### Option 2: Local Development (Windows)

**Backend Setup:**
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend Setup:**
```powershell
cd frontend
npm run dev
```

**Important Notes for Windows:**
- Use PowerShell syntax: `;` instead of `&&` for command chaining
- Run backend from the `backend/` directory, not project root
- Use `127.0.0.1` instead of `0.0.0.0` for host binding to avoid port conflicts
- If you get "port already in use" errors, check for existing processes: `Get-NetTCPConnection -LocalPort 8000`

#### Option 3: Full Docker Stack

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

**Networking notes (dev):**
- The frontend dev server (Vite) proxies API and WebSocket calls to the backend container by service DNS.
- Proxy targets: `/api` and `/ws` → `http://backend:8000` (see `frontend/vite.config.ts`).
- If you change Docker networking or the proxy config, reset the stack to refresh DNS: `docker compose down -v && docker compose up -d`.

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

**Important:** Always run backend tests from the `backend/` directory to ensure proper module imports.

Notes:
- If you omit `-p schemathesis` while disabling auto plugins, contract tests will fail due to a missing `case` fixture.
- Tests do not call external LLMs when `OPENROUTER_API_KEY` is unset; the API returns a local fallback (titles like "Slide 1" with bullets `["Bullet"]`) for speed.

#### Optional live provider tests

To run real calls against providers, set env flags and API keys. These tests are opt‑in and marked; they are skipped by default.

PowerShell (Windows):

```powershell
cd backend
$env:PYTHONPATH=(Get-Location).Path
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
$env:RUN_LIVE_LLM=1; $env:OPENROUTER_API_KEY="sk-or-..."; python -m pytest -q -k live_llm
$env:RUN_LIVE_IMAGES=1; $env:STABILITY_API_KEY="sk-stability-..."; python -m pytest -q -k live_images
```

Bash:

```sh
cd backend
PYTHONPATH=$(pwd) PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 RUN_LIVE_LLM=1 OPENROUTER_API_KEY=sk-or-... \
  python -m pytest -q -k live_llm
PYTHONPATH=$(pwd) PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 RUN_LIVE_IMAGES=1 STABILITY_API_KEY=sk-stability-... \
  python -m pytest -q -k live_images
```

Notes:
- Live tests are labeled with `@pytest.mark.live` and more specific `live_llm` or `live_images` markers.
- They only execute when corresponding `RUN_LIVE_*` flag and API key env var are present.
- To assert real upstream success (no silent fallback), set `OPENROUTER_REQUIRE_UPSTREAM=1` in the same shell before running live LLM tests.

Examples (Windows):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH=(Get-Location).Path
$env:RUN_LIVE_LLM=1; $env:OPENROUTER_API_KEY="sk-or-..."; $env:OPENROUTER_REQUIRE_UPSTREAM=1
# Direct connectivity check
python -m pytest -q -k test_openrouter_direct_chat_completions
# Service and route live tests
python -m pytest -q -k "test_generate_outline_live_llm or test_chat_generate_route_live_llm"
```

Examples (macOS/Linux):

```sh
cd backend
PYTHONPATH=$(pwd) RUN_LIVE_LLM=1 OPENROUTER_API_KEY=sk-or-... OPENROUTER_REQUIRE_UPSTREAM=1 \
  python -m pytest -q -k test_openrouter_direct_chat_completions
PYTHONPATH=$(pwd) RUN_LIVE_LLM=1 OPENROUTER_API_KEY=sk-or-... OPENROUTER_REQUIRE_UPSTREAM=1 \
  python -m pytest -q -k "test_generate_outline_live_llm or test_chat_generate_route_live_llm"
```

### Environment Variables
- Frontend (dev): no env is required. The generated API client uses relative URLs and Vite proxies `/api` and `/ws` to the backend container.
- Frontend (prod or when not using the dev proxy): optionally set `VITE_API_BASE_URL` (e.g., `http://localhost:8000`) in `frontend/.env.local` to direct the client.

### Troubleshooting

#### Backend Won't Start
**Error:** `ModuleNotFoundError: No module named 'app'`
- **Solution:** Make sure you're running the backend from the `backend/` directory, not the project root
- **Command:** `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

**Error:** `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)`
- **Solution:** Port 8000 is already in use. Check for existing processes:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000
  taskkill /PID <PID> /F
  ```
- **Alternative:** Use a different port: `--port 8001`

#### Frontend Can't Connect to Backend
**Error:** `getaddrinfo ENOTFOUND backend`
- **Solution:** The frontend is trying to connect to a Docker service name. For local development, the proxy configuration in `frontend/vite.config.ts` should be enabled:
  ```javascript
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
    '/ws': {
      target: 'http://localhost:8000',
      ws: true,
      changeOrigin: true,
    },
  }
  ```

**Error:** `Port 5173 is already in use`
- **Solution:** Another development server is running. Check for existing processes:
  ```powershell
  Get-NetTCPConnection -LocalPort 5173
  taskkill /PID <PID> /F
  ```
- **Alternative:** Use a different port: `npm run dev -- --port 5174`

#### Image Generation Issues
**Error:** `405 Method Not Allowed` from Stability AI API
- **Solution:** This has been fixed in the latest update. The application now uses the current Stability AI v1 API. If you're still seeing this error, ensure you're using the latest code and have a valid `STABILITY_API_KEY`.

**Error:** Images not loading or showing as placeholders
- **Solution:** Check that your `STABILITY_API_KEY` is valid and the backend can access the Stability AI API. Images are automatically saved to `/app/static/images/` and served via `/static/images/`.

**Error:** DALL-E provider showing as unavailable
- **Solution:** Ensure `OPENAI_API_KEY` is set in `backend/.env` file. The provider status can be checked via `GET /api/v1/slides/providers` endpoint.

**Error:** Provider selection not working in frontend
- **Solution:** Verify that the backend is running and the `/api/v1/slides/providers` endpoint returns both providers as available. Check browser console for any API errors.

#### PowerShell Command Issues
**Error:** `&&` is not a valid statement separator
- **Solution:** Use PowerShell syntax: `;` instead of `&&`
- **Example:** `cd frontend; npm run dev`

#### TanStack Router Import Issues
**Error:** `useLocation is not exported from '@tanstack/react-router'`
- **Solution:** This is a version compatibility issue. The application uses `useRouter` instead:
  ```typescript
  import { useRouter } from '@tanstack/react-router'
  const router = useRouter()
  const location = router.state.location
  ```
- **Note:** The application has been updated to use the correct TanStack Router v2 API

- Backend keys (for live API calls). For simplest usage, put them in `backend/.env` (preferred) or export env vars; no login/JWT required:

  ```env
  # backend/.env (preferred) or environment variables
  OPENROUTER_API_KEY=sk-or-...
  STABILITY_API_KEY=sk-stability-...
  # Optional OpenRouter attribution headers (recommended)
  OPENROUTER_HTTP_REFERER=https://your-site-or-repo
  OPENROUTER_APP_TITLE=AI PowerPoint Generator
  # Optional: require real upstream success in app/tests (disables silent fallback)
  OPENROUTER_REQUIRE_UPSTREAM=0
  ```

  Notes:
  - If keys are not set, the backend now returns a deterministic local fallback for chat outline generation so you can develop and test end‑to‑end without external LLM access.
  - Model IDs follow OpenRouter's current naming, e.g. `openai/gpt-4o-mini` (default) and `openai/gpt-4o`. Ensure any provided `model` is in the allowlist.
  - Be careful with `.env` formatting: lines must start at column 0 (`OPENROUTER_API_KEY=...`)—leading spaces will prevent loading.
  - When deploying publicly, enable authentication and tighten CORS/Rate Limits.

### Dev proxy details
- Vite dev server proxies:
  - `/api` → backend on `http://backend:8000`
  - `/ws`  → backend on `http://backend:8000` (WebSocket path)
- These are configured in `frontend/vite.config.ts`. The generated API client defaults to relative URLs in dev; in production builds, you can provide `VITE_API_BASE_URL`.

### E2E smoke with Playwright MCP (Cursor)
Use the integrated Playwright MCP browser to exercise the app:
- Start the stack: `docker compose up -d`
- Start frontend locally: `cd frontend; npm run dev`
- Open `http://localhost:5173`
- Navigate to Chat and type a prompt, e.g., “Write a 3‑slide deck about observability pillars.”
- Expected result in dev (no API key): assistant reply renders as slide cards (title, bullets, optional image) via `SlidePreview`.
- **Test the Complete Flow**: After generating slides in Chat, click "Slides" in the sidebar to navigate to the Slides section and test PowerPoint generation.
- **Note**: WebSocket connections may show connection errors in dev mode, but API calls work correctly through the proxy.


- If requests fail after changing networking, run: `docker compose down -v && docker compose up -d`

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

- `POST /api/v1/chat/generate` → `SlidePlan[]`
  - Request body (`ChatRequest`): `{ prompt: string, slideCount: number (1–20), model?: string, language?: string, context?: string }`
  - Response: `SlidePlan[]`
  - `SlidePlan`: `{ title: string, bullets: string[], image?: ImageMeta, notes?: string }`
  - `ImageMeta`: `{ url: string, altText: string, provider: string }`
  - Notes: Backend uses OpenRouter `chat/completions` primarily; falls back to legacy route or offline generation if providers fail
  - Possible errors: `429 Too Many Requests`
- `POST /api/v1/auth/login` → `TokenPair`
  - Possible errors: `429 Too Many Requests`
- `POST /api/v1/auth/refresh` → `TokenPair`
  - Possible errors: `401 Unauthorized`, `429 Too Many Requests`
- `GET /api/v1/slides/providers` → Provider status
  - Returns: `{"providers": {"stability-ai": true, "dalle": true}, "available": ["stability-ai", "dalle"]}`
- `POST /api/v1/slides/build` → `PPTXJob`
  - Possible errors: `422 Validation Error`, `429 Too Many Requests`
- `POST /api/v1/slides/generate` → PowerPoint with images
  - Query params: `provider?` (optional: `stability-ai`, `dalle`, or omit for auto)
  - Request body: `PowerPointRequest` with slides and title
  - Response: `PowerPointResponse` with PPTX data and image metadata
- `POST /api/v1/slides/generate-images` → Generate images only
  - Query params: `provider?` (optional: `stability-ai`, `dalle`, or omit for auto)
  - Request body: `SlidePlan[]` array
  - Response: `ImageMeta[]` array with generated image URLs
- `GET /api/v1/slides/download?jobId=<uuid>` → PPTX file download
  - Content-Type: `application/vnd.openxmlformats-officedocument.presentationml.presentation`
  - Filename: `presentation-<jobId>.pptx`
  - Possible errors: `404 Not Found`
- `GET /metrics` → Prometheus text exposition format (`text/plain`)

### Static hosting and image generation

- Static assets are served from `/static` (filesystem: `backend/app/static/`)
- Generated images from Stability AI v1 API are saved under `/static/images/<uuid>.png`
- Public URLs are constructed as `${PUBLIC_BASE_URL}/static/images/<filename>`
- Images are automatically generated using the current Stability AI text-to-image API

Backend config (env) additions:
- `PUBLIC_BASE_URL` (default `http://localhost:8000`)
- `STATIC_URL_PATH` (default `/static`)
- `STATIC_DIR` (default `/app/static` in container)
- `STABILITY_BASE_URL` (default `https://api.stability.ai`)
- `STABILITY_ENGINE_ID` (default `stable-diffusion-xl-1024-v1-0`)
- **Image Provider Configuration**:
  - `OPENAI_API_KEY` - Required for DALL-E image generation
  - `OPENAI_BASE_URL` (default `https://api.openai.com`)
  - `OPENAI_DALLE_MODEL` (default `dall-e-3`)
  - `DEFAULT_IMAGE_PROVIDER` (default `stability-ai`)
  - `IMAGE_PROVIDER_FALLBACK_ORDER` (default `["stability-ai", "dalle"]`)

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
