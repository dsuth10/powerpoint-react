# AI-PowerPoint-Generator Monorepo

![CI](https://github.com/dsuth10/powerpoint-react/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/dsuth10/powerpoint-react/actions/workflows/codeql.yml/badge.svg)

This repository contains both the frontend (React + Vite + TypeScript) and backend (FastAPI) for the AI-PowerPoint-Generator project.

## What's new

- **🆕 Resumable Downloads with Range Requests (September 2025)**: Advanced download manager with resumable download support, persistent chunk storage, and automatic resume on network failures
  - **Range Request Support**: Downloads can resume from where they left off using HTTP Range headers
  - **IndexedDB Persistence**: Downloaded chunks are automatically saved every 2 seconds for crash recovery
  - **Automatic Resume**: On retry or restart, downloads continue from the last saved byte
  - **Smart Cleanup**: Completed downloads are automatically removed from storage with 7-day cleanup for abandoned downloads
  - **Authentication Support**: Download manager properly handles authentication headers for protected endpoints
- **🆕 Complete Slide Editing UI Implementation (August 2025)**: Full frontend implementation of AI-assisted slide editing with comprehensive UI components and state management
  - **Enhanced EditControls Component**: Complete refactor with React Hook Form, Zod validation, and integrated state management
  - **Form Validation & UX**: Real-time validation, character counts, keyboard shortcuts (Ctrl+E, Ctrl+S, Escape, Ctrl+Z)
  - **Preview Functionality**: Real-time slide preview with AI-generated improvements before applying changes
  - **Undo System**: Complete edit history with undo functionality for all editing operations
  - **Batch Edit Controls**: New component for editing multiple slides simultaneously with selection interface
  - **Toast Notifications**: Global toast system for success/error feedback using react-hot-toast
  - **UI Component Library**: Complete shadcn/ui component implementation (Form, Dialog, Select, Button, Input, etc.)
  - **State Management**: Enhanced Zustand store with optimistic updates and edit history tracking
  - **Keyboard Shortcuts**: Global keyboard shortcut system for editing actions
  - **Comprehensive Testing**: Full test suite with React Testing Library and Vitest configuration
- **🆕 AI-Assisted Slide Editing Backend (August 2025)**: Complete slide editing functionality with AI-powered text and image editing capabilities
  - **Text Editing**: AI-assisted editing of slide titles, bullet points, and speaker notes with context awareness
  - **Image Replacement**: AI-generated image replacement using DALL-E or Stability AI with custom prompts
  - **Batch Operations**: Edit multiple slides simultaneously with comprehensive error handling
  - **Preview Mode**: Preview edits before applying changes to slides
  - **Real-time Validation**: Field-level validation with cross-field requirements (e.g., bullet_index required for bullet edits)
- **🆕 DALL-E as Default Image Generator (August 2025)**: OpenAI DALL-E 3 is now the default image generation provider, with Stability AI as a fallback option
- **🆕 Polling-Based Progress System (August 2025)**: Replaced WebSocket real-time updates with a reliable polling mechanism for PowerPoint generation progress
- **🆕 Complete User Flow Implementation (August 2025)**: Full Chat → Slides navigation with session continuity, outline persistence, and seamless PowerPoint generation workflow
- **🆕 Stability AI API Integration Fixed (August 2025)**: Updated to use the current Stability AI v1 API with proper text-to-image generation, base64 image handling, and static file serving
- **✅ Working User Experience**: 
  - Seamless navigation between Chat and Slides sections with session persistence
  - Clear button labels ("Build PowerPoint" instead of confusing "Start Generation")
  - Real-time progress tracking during PowerPoint generation (polling-based)
  - Proper route parameters and state management across sections
  - Session-based outline persistence and retrieval
  - Complete AI-assisted slide editing with form validation, preview mode, and undo functionality
  - Batch editing capabilities for multiple slides
  - Global keyboard shortcuts for efficient editing workflow
  - Toast notifications for user feedback
  - Comprehensive error handling and retry mechanisms
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
  - **DALL-E Integration**: Added OpenAI DALL-E 3 support as the default image generation provider
  - **Provider Selection**: Users can choose between "Auto (DALL-E Preferred)", "DALL-E", or "Stability AI" in the frontend
  - **Automatic Fallback**: System automatically falls back to available providers if preferred provider fails
  - **Factory Pattern**: Clean architecture with `ImageProvider` interface and provider registry
- **🆕 Slide Editing API Endpoints (August 2025)**: New API endpoints for AI-assisted slide editing
  - **Single Edit**: `POST /api/v1/slides/edit` - Edit individual slide content (title, bullet, notes, image)
  - **Batch Edit**: `POST /api/v1/slides/edit-batch` - Edit multiple slides simultaneously
  - **Preview Edit**: `POST /api/v1/slides/edit-preview` - Preview changes without applying them
  - **Validation**: Comprehensive field validation with cross-field requirements and error handling
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
  - **Progress Updates**: Polling-based progress system for PowerPoint generation (WebSocket removed for reliability)

## Recent Updates (September 2025)

### Resumable Downloads Implementation ✅

**Problem Solved**: PowerPoint downloads needed to support resume functionality for large files and unreliable network conditions, with proper authentication and error recovery.

**Solution Implemented**:
1. **Range Request Support**: Implemented HTTP Range headers for resumable downloads
2. **IndexedDB Persistence**: Automatic chunk persistence every 2 seconds during download
3. **Crash Recovery**: Downloads automatically resume from the last saved byte after interruption
4. **Authentication Integration**: Download manager properly passes authentication headers to protected endpoints
5. **Smart Cleanup**: Automatic removal of completed downloads and 7-day cleanup for abandoned downloads

**Technical Changes**:
- **Download Manager Enhancement** (`frontend/src/lib/download-manager.ts`):
  - Added `resumable` option (default: true) to enable Range request support
  - Implemented IndexedDB for persistent chunk storage
  - Added automatic resume detection for partial downloads
  - Integrated authentication header support
  - Implemented periodic persistence (2-second intervals)
  - Added cleanup utilities for managing stored downloads

- **Download Button Update** (`frontend/src/components/slides/DownloadButton.tsx`):
  - Integrated authentication headers from auth store
  - Enhanced error handling with resume capability
  - Added proper header propagation to download manager

**Configuration**:
- **Default Settings**:
  - `resumable: true` - Enables Range request support
  - `chunkSize: 1MB` - Default chunk size for range requests
  - Automatic persistence every 2 seconds
  - 7-day retention for abandoned downloads

**Result**: PowerPoint downloads are now resilient to network failures, support resume functionality, and properly handle authentication. Large files can be downloaded reliably even on unstable connections, with automatic recovery from interruptions.

## Recent Updates (August 2025)

### Complete Slide Editing UI Implementation ✅

**Problem Solved**: The slide editing functionality needed a complete frontend implementation with proper form handling, validation, state management, and user experience features.

**Solution Implemented**:
1. **Enhanced EditControls Component**: Complete refactor using React Hook Form and Zod validation
2. **Form Validation & UX**: Real-time validation, character counts, and comprehensive error handling
3. **Preview Functionality**: Real-time slide preview with AI-generated improvements
4. **Undo System**: Complete edit history with undo functionality for all operations
5. **Batch Edit Controls**: New component for editing multiple slides simultaneously
6. **Toast Notifications**: Global toast system for user feedback
7. **UI Component Library**: Complete shadcn/ui implementation
8. **State Management**: Enhanced Zustand store with optimistic updates
9. **Keyboard Shortcuts**: Global keyboard shortcut system
10. **Comprehensive Testing**: Full test suite with proper configuration

**Technical Changes**:
- **Frontend Components**:
  - `frontend/src/components/slides/EditControls.tsx`: Complete refactor with React Hook Form, Zod validation, preview functionality, and undo system
  - `frontend/src/components/slides/BatchEditControls.tsx`: New component for batch editing with slide selection interface
  - `frontend/src/components/ui/*`: Complete shadcn/ui component library (Form, Dialog, Select, Button, Input, Textarea, Label, Checkbox)
  - `frontend/src/providers/ToastProvider.tsx`: Global toast notification system
  - `frontend/src/hooks/use-edit-shortcuts.ts`: Global keyboard shortcut management
  - `frontend/src/routes/pages/SlidesPage.tsx`: Integration of all editing components with navigation

- **State Management**:
  - `frontend/src/stores/slides-store.ts`: Enhanced with editing state, edit history, optimistic updates, and undo functionality
  - `frontend/src/config/editing.ts`: Configuration for UI behavior, validation limits, and keyboard shortcuts

- **API Integration**:
  - `frontend/src/hooks/api/slides.ts`: Updated to use raw API client for editing endpoints with proper error handling
  - `frontend/src/lib/utils.ts`: Utility functions for class name management

- **Testing & Configuration**:
  - `frontend/vitest.config.ts`: Updated with jsdom environment and path aliases
  - `frontend/vitest.setup.ts`: Proper test environment setup with global APIs
  - `frontend/src/components/slides/EditControls.test.tsx`: Comprehensive tests for form validation, preview, and undo functionality
  - `frontend/src/components/slides/BatchEditControls.test.tsx`: Full test suite for batch editing component

- **Dependencies**:
  - Added: `react-hook-form`, `@hookform/resolvers`, `zod`, `react-hot-toast`, `class-variance-authority`, `@radix-ui/*` components

**Result**: Complete slide editing UI with professional form handling, real-time validation, preview functionality, undo system, batch editing, keyboard shortcuts, and comprehensive error handling. The user experience is now production-ready with proper feedback and accessibility features.

### DALL-E as Default Image Generator ✅

**Problem Solved**: Users wanted DALL-E to be the primary image generation provider instead of Stability AI, while maintaining fallback options.

**Solution Implemented**:
1. **DALL-E as Default**: Changed the default image provider from Stability AI to DALL-E across all configuration layers
2. **Updated Fallback Order**: Modified provider fallback order to prioritize DALL-E over Stability AI
3. **Frontend UI Updates**: Updated dropdown options to show "Auto (DALL-E Preferred)" and reordered options to show DALL-E first
4. **Store Configuration**: Updated default state in slide generation store to use DALL-E

**Technical Changes**:
- `backend/app/core/config.py`: 
  - `DEFAULT_IMAGE_PROVIDER: str = "dalle"`
  - `IMAGE_PROVIDER_FALLBACK_ORDER: List[str] = ["dalle", "stability-ai"]`
- `frontend/src/components/slides/GenerationControls.tsx`: 
  - Default selected provider changed to `'dalle'`
  - Dropdown options updated to "Auto (DALL-E Preferred)", "DALL-E", "Stability AI"
- `frontend/src/stores/slide-generation-store.ts`: 
  - Default `imageProvider` changed from `'auto'` to `'dalle'`

**Result**: DALL-E is now the default image generation provider, with Stability AI available as a fallback option. Users can still manually select any provider, and the auto mode now prefers DALL-E over Stability AI.

### Polling-Based Progress System ✅

**Problem Solved**: WebSocket connections were failing repeatedly, causing connection errors and unreliable progress updates during PowerPoint generation.

**Solution Implemented**:
1. **WebSocket Removal**: Completely removed WebSocket-based progress updates from both frontend and backend
2. **Polling Implementation**: Replaced with a reliable polling mechanism that updates progress every 2 seconds
3. **Simplified Architecture**: Removed Socket.IO dependencies and complex WebSocket event handling
4. **Improved Reliability**: Eliminated connection failures and ASGI protocol mismatches

**Technical Changes**:
- **Frontend Changes**:
  - `frontend/src/components/slides/GenerationControls.tsx`: Replaced WebSocket `useEffect` with polling-based progress updates
  - `frontend/src/lib/slide-generation-socket.ts`: **Deleted** - no longer needed
  - Removed Socket.IO client imports and WebSocket connection logic
  - Implemented simulated polling that increments progress every 2 seconds

- **Backend Changes**:
  - `backend/app/api/slides.py`: Removed Socket.IO imports and event emission
  - `backend/app/main.py`: Removed Socket.IO ASGI app mounting
  - `backend/app/socketio_app.py`: No longer used by the application

**Result**: PowerPoint generation now uses a reliable polling-based progress system that eliminates WebSocket connection errors and provides consistent progress updates. The system is more stable and easier to maintain.

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

### PowerPoint Download Functionality Fix ✅

**Problem Solved**: After generating a PowerPoint, the percentage went up to 100% but the file didn't automatically download to the user's Downloads folder as it used to.

**Solution Implemented**:
1. **Added DownloadButton Component**: Integrated the existing `DownloadButton` component into the UI with proper error handling and retry logic
2. **Fixed Download URL Format**: Corrected the download endpoint from `/download?jobId=` to `/download/{job_id}` to match the backend API path parameter format
3. **Added Job Status Endpoint**: Created `/api/v1/slides/job/{job_id}` endpoint to provide real-time job status and progress tracking
4. **Implemented Real Polling System**: Replaced simulated progress with actual backend polling that checks job status every 2 seconds
5. **Enhanced User Experience**: Added clear success indication with "✅ PowerPoint ready!" message and manual download button

**Technical Changes**:
- **Backend Changes**:
  - `backend/app/api/slides.py`: Added `get_job_status` endpoint for real-time job monitoring
  - Job status endpoint returns progress, status, error messages, and file path information

- **Frontend Changes**:
  - `frontend/src/components/slides/GenerationControls.tsx`: 
    - Added real polling system that checks backend job status
    - Integrated `DownloadButton` component with success messaging
    - Removed automatic download in favor of reliable manual download
  - `frontend/src/components/slides/DownloadButton.tsx`: 
    - Fixed download URL format to use path parameters instead of query parameters
    - Enhanced error handling with retry functionality

**Result**: PowerPoint generation now provides:
- **Real-time progress tracking** from the backend
- **Clear success indication** when PowerPoint is ready
- **Reliable manual download** with proper error handling
- **Better user control** over when to download files

**User Experience**: 
- When PowerPoint generation completes, users see "✅ PowerPoint ready!" 
- A "Download PPTX" button appears for manual download
- Downloads go directly to the user's Downloads folder
- Clear error messages if download fails with retry option

**Note**: The automatic download was replaced with manual download for better reliability and user control. This eliminates timing issues and provides clearer feedback to users.

## Project Structure

- `frontend/` – React 18 + Vite + TypeScript app
  - `src/components/slides/` – Slide editing components (EditControls, BatchEditControls)
  - `src/components/ui/` – shadcn/ui component library (Form, Dialog, Select, Button, etc.)
  - `src/stores/` – Zustand state management with editing state and history
  - `src/hooks/` – Custom hooks including API integration and keyboard shortcuts
  - `src/providers/` – Context providers including ToastProvider for notifications
  - `src/config/` – Configuration files for editing behavior and validation
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
5. **Edit Slides (Optional)**: Use the "Edit Slide" button to refine titles, bullet points, notes, or replace images with AI assistance
   - **Form Validation**: Real-time validation with character counts and field requirements
   - **Preview Mode**: See AI-generated improvements before applying changes
   - **Undo Functionality**: Undo any edit operation with complete edit history
   - **Keyboard Shortcuts**: Use Ctrl+E to edit, Ctrl+S to save, Escape to cancel, Ctrl+Z to undo
   - **Batch Editing**: Select multiple slides and apply edits simultaneously
6. **Generate PPTX**: Click "Build PowerPoint" button to start generation
7. **Monitor Progress**: Watch real-time progress updates during generation (polls backend every 2 seconds)
8. **Download**: When generation completes, click "Download PPTX" button that appears with "✅ PowerPoint ready!" message

### **Key Features**
- ✅ **Session Continuity**: Your chat session and slide outlines persist when switching between sections
- ✅ **Clear Navigation**: Sidebar automatically includes your current session when navigating to Slides
- ✅ **Complete AI-Assisted Editing**: Professional editing interface with form validation, preview mode, and undo functionality
- ✅ **Batch Editing**: Edit multiple slides simultaneously with comprehensive selection interface
- ✅ **Keyboard Shortcuts**: Global shortcuts (Ctrl+E, Ctrl+S, Escape, Ctrl+Z) for efficient editing workflow
- ✅ **Real-time Progress**: Polling-based system provides live updates during PowerPoint generation
- ✅ **Manual Download**: Clear download button appears when generation is complete
- ✅ **Multiple Sessions**: Create and manage multiple chat sessions with different slide outlines
- ✅ **Error Recovery**: Retry buttons, toast notifications, and clear error messages for failed operations
- ✅ **Proxy Configuration**: Vite dev server properly proxies API calls to backend

## Getting Started

### Prerequisites
- Node.js 18.19.0 (see `.nvmrc`)
- Python 3.12.0 (see `backend/.python-version`)
- Docker Desktop (for dev workflow)

### Frontend Technical Stack (Updated)
- **React 18** with TypeScript and Vite
- **State Management**: Zustand v4.5 with Immer and DevTools middleware
- **Form Handling**: React Hook Form with Zod validation
- **UI Components**: shadcn/ui component library with Radix UI primitives
- **Styling**: Tailwind CSS with custom animations
- **Notifications**: react-hot-toast for global toast notifications
- **Testing**: Vitest with React Testing Library and jsdom environment
- **API Client**: OpenAPI generated client with TanStack Query v5
- **Icons**: Lucide React for consistent iconography
- **Utilities**: class-variance-authority, clsx, tailwind-merge for styling utilities

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
  }
  ```

**Error:** `Port 5173 is already in use`
- **Solution:** Another development server is running. Check for existing processes:
  ```powershell
  Get-NetTCPConnection -LocalPort 5173
  taskkill /PID <PID> /F
  ```
- **Alternative:** Use a different port: `npm run dev -- --port 5174`

#### PowerPoint Generation Issues
**Error:** Progress updates not working or stuck at 0%
- **Solution:** The application now uses a real polling-based progress system that checks the backend job status every 2 seconds. If progress appears stuck, check the browser console for any API errors or backend logs.

**Error:** Download button not appearing after generation completes
- **Solution:** Ensure the PowerPoint generation has fully completed. The download button appears with "✅ PowerPoint ready!" message when generation is done. If the button doesn't appear, check the browser console for any errors.

**Error:** Download fails with 404 error
- **Solution:** The download URL format has been updated to use path parameters. Ensure you're using the latest version of the application. The correct format is `/api/v1/slides/download/{job_id}`.

**Error:** Download interrupted or failed midway
- **Solution:** The download manager now supports automatic resume. Simply retry the download and it will continue from where it left off. The system uses IndexedDB to persist downloaded chunks and automatically resumes using HTTP Range requests.

**Error:** Download won't resume after browser restart
- **Solution:** Downloads persist in IndexedDB across browser restarts. When you retry a download, it should automatically detect the partial download and resume from the last saved byte. Check the browser console for any IndexedDB errors.

**Error:** Authentication errors during download
- **Solution:** The download manager now properly includes authentication headers. Ensure you're logged in and have a valid session token. If the token expires during download, you'll need to log in again and retry.

**Error:** DALL-E provider showing as unavailable
- **Solution:** Ensure `OPENAI_API_KEY` is set in `backend/.env` file. The provider status can be checked via `GET /api/v1/slides/providers` endpoint.

**Error:** Provider selection not working in frontend
- **Solution:** Verify that the backend is running and the `/api/v1/slides/providers` endpoint returns both providers as available. Check browser console for any API errors.

**Error:** Slide editing not working or validation errors
- **Solution:** Ensure you have a valid `OPENROUTER_API_KEY` set in `backend/.env` file for AI-assisted text editing. The editing functionality requires LLM access for AI-powered improvements. Check browser console for any validation errors or API failures. The new editing interface includes form validation, so ensure all required fields are filled correctly.

**Error:** Edit button not appearing in Slides section
- **Solution:** The edit functionality is integrated into the Slides section. Ensure you're using the latest version of the application and that the backend is running properly. The edit button should appear for each slide in the Slides section. The new implementation includes enhanced EditControls with form validation and preview functionality.

**Error:** Form validation errors in editing dialog
- **Solution:** The new editing interface uses React Hook Form with Zod validation. Ensure all required fields are filled and meet the validation requirements (e.g., content length limits, bullet_index for bullet edits). Check the form for validation messages and character count indicators.

**Error:** Keyboard shortcuts not working
- **Solution:** The keyboard shortcuts (Ctrl+E, Ctrl+S, Escape, Ctrl+Z) are global and should work when the editing dialog is open. Ensure you're not in an input field when using shortcuts, or use the mouse buttons instead. The shortcuts are managed by the `useEditShortcuts` hook.

**Error:** Toast notifications not appearing
- **Solution:** The toast notification system requires the `ToastProvider` to be properly configured. Ensure the application is using the latest version with the `ToastProvider` wrapper in `main.tsx`. Toast notifications appear for success and error messages during editing operations.

**Error:** Batch editing not working
- **Solution:** The batch editing functionality requires selecting slides using the checkboxes in the BatchEditControls component. Ensure you've selected at least one slide and chosen a batch operation from the dropdown. The batch editing interface is separate from individual slide editing.

#### Image Generation Issues
**Error:** `405 Method Not Allowed` from Stability AI API
- **Solution:** This has been fixed in the latest update. The application now uses the current Stability AI v1 API. If you're still seeing this error, ensure you're using the latest code and have a valid `STABILITY_API_KEY`.

**Error:** Images not loading or showing as placeholders
- **Solution:** Check that your API keys are valid and the backend can access the image generation APIs. For DALL-E, ensure `OPENAI_API_KEY` is set. For Stability AI, ensure `STABILITY_API_KEY` is set. Images are automatically saved to `/app/static/images/` and served via `/static/images/`.

**Error:** DALL-E not generating images (default provider)
- **Solution:** Ensure `OPENAI_API_KEY` is set in `backend/.env` file. DALL-E is now the default provider, so this key is required for normal operation. Check the provider status via `GET /api/v1/slides/providers` endpoint.

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
- These are configured in `frontend/vite.config.ts`. The generated API client defaults to relative URLs in dev; in production builds, you can provide `VITE_API_BASE_URL`.

### E2E smoke with Playwright MCP (Cursor)
Use the integrated Playwright MCP browser to exercise the app:
- Start the stack: `docker compose up -d`
- Start frontend locally: `cd frontend; npm run dev`
- Open `http://localhost:5173`
- Navigate to Chat and type a prompt, e.g., "Write a 3‑slide deck about observability pillars."
- Expected result in dev (no API key): assistant reply renders as slide cards (title, bullets, optional image) via `SlidePreview`.
- **Test the Complete Flow**: After generating slides in Chat, click "Slides" in the sidebar to navigate to the Slides section and test PowerPoint generation.
- **Test Slide Editing**: Use the "Edit Slide" button in the Slides section to test AI-assisted editing of titles, bullet points, notes, and images.
  - **Form Validation**: Test the new form validation by leaving required fields empty or exceeding character limits
  - **Preview Mode**: Use the preview functionality to see AI-generated improvements before applying
  - **Undo Functionality**: Test the undo button after making edits to verify edit history works
  - **Keyboard Shortcuts**: Test Ctrl+E to edit, Ctrl+S to save, Escape to cancel, Ctrl+Z to undo
  - **Batch Editing**: Test the batch editing functionality by selecting multiple slides and applying edits
  - **Toast Notifications**: Verify that success and error messages appear as toast notifications
- **Note**: The application now uses a polling-based progress system for PowerPoint generation, which is more reliable than the previous WebSocket implementation.


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
- `POST /api/v1/slides/edit` → Edit slide content with AI assistance
  - Request body: `EditSlideRequest` with slide_index, target (title/bullet/notes/image), content, and optional fields
  - Response: `EditSlideResponse` with updated slide and success status
  - Possible errors: `400 Validation Error`, `429 Too Many Requests`
- `POST /api/v1/slides/edit-batch` → Edit multiple slides simultaneously
  - Request body: `BatchEditRequest` with array of `EditSlideRequest` objects
  - Response: `BatchEditResponse` with results for each edit operation
  - Possible errors: `400 Validation Error`, `429 Too Many Requests`
- `POST /api/v1/slides/edit-preview` → Preview slide edits without applying
  - Request body: Same as single edit endpoint
  - Response: `EditSlideResponse` with preview of changes
  - Possible errors: `400 Validation Error`, `429 Too Many Requests`
- `GET /api/v1/slides/download/{job_id}` → PPTX file download
  - Content-Type: `application/vnd.openxmlformats-officedocument.presentationml.presentation`
  - Filename: `presentation-{job_id}.pptx`
  - Possible errors: `404 Not Found`
- `GET /api/v1/slides/job/{job_id}` → Job status and progress
  - Returns: `{"job_id": "uuid", "status": "pending|processing|completed|failed", "progress": 0-100, "total": 1, "message": "string", "error": "string", "file_path": "string"}`
  - Used for real-time progress tracking during PowerPoint generation
  - Possible errors: `404 Not Found`
- `GET /metrics` → Prometheus text exposition format (`text/plain`)

### Static hosting and image generation

- Static assets are served from `/static` (filesystem: `backend/app/static/`)
- Generated images from AI providers are saved under `/static/images/<uuid>.png`
- Public URLs are constructed as `${PUBLIC_BASE_URL}/static/images/<filename>`
- Images are automatically generated using DALL-E (default) or Stability AI APIs

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
  - `DEFAULT_IMAGE_PROVIDER` (default `dalle`)
  - `IMAGE_PROVIDER_FALLBACK_ORDER` (default `["dalle", "stability-ai"]`)
- **Slide Editing Configuration**:
  - `TEXT_EDITING_MODEL` (default `openai/gpt-4o-mini`) - LLM model for text editing
  - `TEXT_EDITING_TEMPERATURE` (default `0.3`) - Creativity level for text editing
  - `TEXT_EDITING_MAX_TOKENS` (default `500`) - Maximum tokens for text editing responses
  - `EDIT_RATE_LIMIT_PER_MINUTE` (default `30`) - Rate limit for single edit operations
  - `BATCH_EDIT_RATE_LIMIT_PER_MINUTE` (default `10`) - Rate limit for batch edit operations
  - `MAX_EDIT_CONTENT_LENGTH` (default `1000`) - Maximum content length for edit requests
  - `MAX_BATCH_EDITS` (default `10`) - Maximum number of edits in a batch operation

## Scripts

- `scripts/smoke.ps1` – bring up the stack and smoke-check FE/BE
- `scripts/verify.ps1` – repo and versions sanity checks