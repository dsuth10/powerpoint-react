# Backend Module Guide (Revised 2025-07-12)

---

## Quick Start

```bash
# 1. (Recommended) Use Docker for all development, testing, and quality checks
#    This ensures cross-platform reliability and matches CI/CD.
#    See below for Docker usage instructions.

# 2. (Optional) Local venv setup for advanced users only
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\Activate  # Windows PowerShell

# 3. Install production dependencies (pinned in requirements.txt)
pip install -r requirements.txt

# 4. Start the development server (auto-reload)
fastapi dev --app app.main:app
```

> **Note:** All CLI examples assume your working directory is `backend/`.
> **All contributors must use Docker or CI for all quality checks and development.**

---

## Directory Layout

```
backend/
└── app/
    ├── main.py           # FastAPI application instance
    ├── api/              # Versioned API route modules
    ├── models/           # Pydantic v2 models
    ├── services/         # Business-logic services (LLM, images, pptx)
    ├── socketio_app.py   # python-socketio server mounted at /ws
    └── core/             # Config, logging, error handlers
```

All import paths use the `app.` prefix, e.g. `from app.services.llm import process_chat`.

---

## Dependency Manifest (`requirements.txt`)

The full list is generated from `versions.md`. Below is an excerpt of the **runtime** subset:

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
pydantic-settings==2.3.0
httpx==0.27.0
tenacity==8.2.3
limits==3.12.0
loguru==0.7.2
prometheus-fastapi-instrumentator==7.0.0
python-socketio==5.11.0
python-pptx==0.6.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

*Removed packages*: `flask-socketio`, `sqlalchemy`, `alembic`, `asyncpg`, `runware-sdk-python` (not available on PyPI).

---

## Docker Usage for Backend Development

All backend development, testing, and quality checks must be run in Docker or CI for consistency and cross-platform reliability.

- **Build and run backend in Docker:**
  ```sh
  docker compose up -d backend
  ```
- **Run lint, format, type check, and tests in Docker:**
  ```sh
  docker compose run --rm backend ruff .
  docker compose run --rm backend black --check .
  docker compose run --rm backend mypy .
  docker compose run --rm backend pytest --cov=backend/app --cov-report=term-missing
  ```
- **Auto-format code:**
  ```sh
  docker compose run --rm backend black .
  ```

> **Troubleshooting (Windows):**
> - If you encounter permission errors or issues with cache/coverage files, ensure all directories are writable and not locked by another process.
> - Always use Docker for all quality checks to avoid platform-specific issues.

---

## Running Tests

```bash
pytest -q     # Runs unit + integration tests (≥ 90 % coverage gate)
```

Coverage configuration is defined in `pytest.ini`.

---

## Environment Variables

Refer to `versions.md` for the canonical list. Minimum required to start locally:

```
PROJECT_ENV=development
OPENROUTER_API_KEY=your-openrouter-key
RUNWARE_API_KEY=your-runware-key
JWT_SECRET_KEY=local-secret
```

---

## Real-time Communication

The `python-socketio` server is initialised in **ASGI** mode and mounted under `/ws`.

```python
# app/socketio_app.py
import socketio
from fastapi import FastAPI

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = FastAPI()
app.mount("/ws", socketio.ASGIApp(sio, socketio_path="socket.io"))
```

Frontend clients connect via:
```ts
io(import.meta.env.VITE_WS_URL, { path: '/ws/socket.io' })
```

---

## Performance Targets

- **API latency P95**: ≤ 400 ms (production) / ≤ 600 ms (staging)
- **Slide generation turnaround**: ≤ 30 s for a 5-slide deck

See Stage 5 SLO dashboard for live metrics.

---

## CI / CD

The backend participates in the unified `CI-CD` GitHub Actions workflow. Key steps:

| Step | Tool | Gate |
|------|------|------|
| Lint | `ruff`, `black` | Zero errors |
| Type check | `mypy` | Zero errors |
| Test | `pytest`, `pytest-asyncio`, `respx`, `python-socketio` | Coverage ≥ 90 % |
| Contract | `schemathesis` | All endpoints conform to OpenAPI |
| Performance | `k6` | P95 < 800 ms |
| Build | Docker multi-stage | Non-root image ≤ 250 MB |
| Scan | `bandit`, `trivy` | No HIGH / CRITICAL CVEs |

All quality gates are enforced in CI. See `.github/workflows/ci.yml` for details.

---

## Stage 1 Foundation Completion

- Backend is fully Dockerized and all quality gates pass in Docker and CI.
- All dependencies are pinned and enforced via `versions.md`.
- All code is auto-formatted and type-checked.
- Contributors must read the planning documents before making changes.
- See `architecture-overview.md` and `README.md` for system context and onboarding.

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-07-20 | Stage 2 backend complete: All endpoints, models, services, middleware, observability, contract tests, k6 scripts, and CI/CD (Bandit, Trivy) implemented and passing. | AI Assistant |
