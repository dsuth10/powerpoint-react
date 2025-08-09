# Stage 2 · Backend Development (Updated 2025-07-12)

_Primary Goal_: Implement a fully-typed, well-tested FastAPI service that exposes all contract-compliant endpoints required by the AI-PowerPoint-Generator frontend and background services.  This stage covers authentication, business logic services, external integrations, observability hooks, and an automated CI pipeline achieving ≥ 90 % unit-test coverage.

---

## **Stage 1 Foundation Compliance (New Requirements)**
- **All development, testing, and quality checks must be run in Docker or CI for consistency and cross-platform reliability.**
- **All dependencies must be pinned in `versions.md` before any change.** New dependencies require justification in PRs.
- **WebSocket bridge uses only `python-socketio` (no Flask-SocketIO).**
- **All tests, lint, and type checks must pass in Docker and CI.**
- **All contributors must read `versions.md`, `architecture-overview.md`, and `backend-README.md` before starting Stage 2 work.**
- **Troubleshooting:** If switching between host and Docker, always delete `venv`/`node_modules` and reinstall in Docker to avoid native module issues. All quality checks must be run in Docker or CI for consistency.
- **Makefile targets must be Docker-compatible or have Docker Compose equivalents.**
- **CI/CD:** All quality gates are enforced in the unified GitHub Actions workflow (`.github/workflows/ci.yml`).
- **All version numbers, tool names, and workflow steps must match Stage 1 (Python 3.12.0, Node.js 18.19.0, FastAPI 0.111.0, etc.).**

---

## 1. Entry & Exit Criteria

| Phase Gate | Criteria |
|------------|----------|
| **Entry** | • Stage 1 repository, tooling, and CI skeleton are complete<br>• Engineering environments (local + Docker) are functional<br>• Product team has signed off on API surface (OpenAPI draft v0.9)<br>• Budgeted resource allocation: 1 BE TL + 2 BE engineers + 1 SDET |
| **Exit** | • All endpoints implement v1.0 OpenAPI schema and pass contract tests<br>• ≥ 90 % line + branch coverage on `backend/`<br>• Security scan (Bandit) shows _no_ high-severity issues<br>• Slide outline requests complete P95 < 800 ms (in staging)<br>• CI pipeline green; Docker image `backend:1.0.0` pushed to registry |

---

## 2. Work-Breakdown Structure (WBS)

| ID | Task | Lead | Estimates | Depends on |
|----|------|------|-----------|------------|
| **2.1** | Domain modelling in **Pydantic v2** (ChatRequest, SlidePlan, ImageMeta, PPTXJob) | BE-1 | 6 h | 1.0 |
| **2.2** | **LLM service** wrapper (`services/llm.py`) with OpenRouter integration + retry logic | BE-2 | 8 h | 2.1 |
| **2.3** | **Image service** wrapper (`services/images.py`) for Runware API | BE-2 | 8 h | 2.2 |
| **2.4** | **PPTX builder** (`services/pptx.py`) using python-pptx | BE-1 | 12 h | 2.1 |
| **2.5** | **Auth subsystem** — JWT issuance, passwordless magic-link endpoint, FastAPI deps | BE-3 | 10 h | 1.0 |
| **2.6** | **API routes** `/chat`, `/slides`, `/auth`, `/health` (OpenAPI tags, response models) | BE-1 | 14 h | 2.1,2.2,2.3,2.5 |
| **2.7** | **WebSocket bridge** via python-socketio for real-time progress | BE-2 | 8 h | 2.4 |
| **2.8** | **Error & rate-limit middleware** (`core/errors.py`, `core/rate_limit.py`) | BE-3 | 6 h | 2.6 |
| **2.9** | **Observability hooks** — structlog JSON logging, Prometheus metrics, /metrics route | BE-3 | 6 h | 2.6 |
| **2.10** | **Testing harness** — pytest, pytest-asyncio, respx, socketio test client | SDET | 10 h | tasks 2.1-2.7 |
| **2.11** | **Seed contract tests** (OpenAPI + schemathesis) | SDET | 6 h | 2.6 |
| **2.12** | **Performance scripts** (k6) for slide generation & chat | SDET | 6 h | 2.4,2.6 |
| **2.13** | **CI jobs** — unit, integration, coverage gate, Docker build, image scan | DevOps | 6 h | 2.10 |

---

## 3. Detailed Implementation Steps

### 3.1 Domain Modelling (Task 2.1)
1. Create `backend/models/` package with sub-modules per domain (_chat.py_, _slides.py_, _common.py_).
2. Enforce **Pydantic v2** strict mode (`model_config = {"strict": True}`) for early validation.
3. Write exhaustive docstrings + examples to auto-propagate into OpenAPI docs.
4. Add unit tests ensuring `.model_dump()` yields camelCase keys required by TypeScript clients.

### 3.2 External Service Wrappers (Tasks 2.2–2.3)
1. Implement async HTTP factories using `httpx.AsyncClient` with connection pooling (max = 100, keep-alive).
2. Centralise exponential-back-off decorator (`@retry(stop=stop_after_attempt(3), wait=wait_exponential())`).
3. Mask secrets (`OPENROUTER_KEY`, `RUNWARE_API_KEY`) in logs via custom log filter.
4. Provide typed exceptions (`LLMError`, `ImageError`) bubbling to route layer.

### 3.3 PPTX Builder (Task 2.4)
1. Prototype slide layout mapping → title/body + optional image placeholder using `python-pptx` master template.
2. Embed speaker notes when present.
3. Persist output to `/tmp/{uuid}.pptx`; return `Path`.
4. Include resiliency: if image download fails, insert branded placeholder asset.

### 3.4 Authentication & Security (Task 2.5, 2.8)
1. Issue **JWT** with HS256 signing; 15-min access + 24-h refresh tokens.
2. Passwordless magic-link flow: POST email → send signed one-time URL (SES mock in dev).
3. Rate limit: `X-Forwarded-For` aware sliding-window (100 req / 15 min) via `limits` package.
4. Add CORS middleware restricted to `VITE_APP_URL` & staging domain.
5. Static analysis with **Bandit**; integrate into CI.

### 3.5 API Routes (Task 2.6)
- `/chat/generate` POST → returns `ChatResponse`
- `/slides/build` POST (async) → returns `jobId`; progress via WS `slide:progress`; final via `slide:completed` w/ URL.
- `/auth/login` POST, `/auth/refresh` POST.
- `/health` GET returns build metadata + git SHA.

### 3.6 WebSocket Bridge (Task 2.7)
1. Mount python-socketio under `/ws` with CORS parity.
2. Emit `slide:progress`, `slide:completed`, `error` events.
3. Add disconnect handler → resume retry logic client side.

### 3.7 Observability (Task 2.9)
1. Structured logs via `loguru` + `uvicorn.access` JSON.
2. Prometheus fastapi-instrumentator exporter; expose `/metrics`.
3. Sentry SDK (env-gated) for exception tracking.

### 3.8 Testing Strategy (Tasks 2.10–2.12)
| Layer | Tooling | Coverage Target |
|-------|---------|-----------------|
| **Unit** | pytest, pytest-asyncio | ≥ 90 % lines |
| **Service** | Respx for OpenRouter/Runware mocks | 100 % happy + sad paths |
| **Contract** | schemathesis vs `/openapi.json` | All hypothesis tests pass |
| **WebSocket** | python-socketio test client | All events received |
| **Performance** | k6 scripted (chat & slide) | P95 < 800 ms |

Add `pytest --maxfail=1 --disable-warnings` gate in CI.

### 3.9 CI/CD (Task 2.13)
1. Extend existing GH Actions matrix (`python: [3.12.0]`, OS: ubuntu-latest).
2. Jobs: _install_, _lint_ (ruff, black --check), _unit_, _integration_, _coverage_ (Codecov), _docker_, _trivy scan_.
3. Push image `ghcr.io/org/pptx-backend:${{ github.sha }}` on main.
4. Trigger Stage 4 E2E workflow via repository dispatch.

---

## 4. Interfaces & Dependencies

```
Frontend  ⇄  FastAPI  ⇄  OpenRouter LLM
          ⇄           ⇄  Runware Images
          ⇄  python-socketio (WS)
```

All HTTP response bodies are typed by OpenAPI; TypeScript clients regenerated nightly (cron) to catch drift.

---

## 7. Acceptance Tests (excerpt)

1. **Generate Chat** – POST `/chat/generate` with prompt ⇒ 200 + `slidePlan.length == n`.
2. **Build Slides** – POST `/slides/build` ⇒ jobId; WS emits `slide:completed` with downloadable URL within 30 s for a 5-slide deck.
3. **Auth Refresh** – Expired access token + valid refresh ⇒ 200 new token pair.
4. **Rate Limit** – >100 requests / 15 min from same IP ⇒ 429.
5. **Observability** – `/metrics` exposes `http_request_duration_seconds_count` metric.

---

## 8. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| OpenRouter latency spikes | Slow UX | Med | Cache outline per prompt hash 1 h |
| Runware quota exhaustion | Image failures | Low | Secondary provider fallback |
| JWT key leak | Account takeover | Low | Rotate keys weekly, use AWS KMS |
| Type drift between FE/BE | 500s in prod | Med | Nightly type-gen + contract tests |
| Docker image CVE | Security incident | Med | Daily trivy scheduled scan |

---

## 9. Deliverables Checklist

- [x] `backend/` source code tasks 2.1 – 2.9 merged to _main_
- [x] Unit + integration test suites pass locally & CI
- [x] Coverage badge ≥ 90 %
- [x] Docker image `backend:1.0.0` published
- [x] CHANGELOG updated
- [x] Stage 3 kickoff meeting scheduled
- [x] All quality gates pass in Docker and CI
- [x] All dependencies pinned in `versions.md`
- [x] All contributors have reviewed planning documents and onboarding

---

## Change Log
| Date | Change | Author |
|------|--------|--------|
| 2025-07-20 | Stage 2 backend complete: All endpoints, models, services, middleware, observability, contract tests, k6 scripts, and CI/CD (Bandit, Trivy) implemented and passing. | AI Assistant |

---

### Appendix A · ENV Template
```env
OPENROUTER_KEY=xxxx
RUNWARE_API_KEY=xxxx
JWT_SECRET=change-me
PROMETHEUS_METRICS=true
PROJECT_ENV=development
```

### Appendix B · Makefile Targets
```makefile
lint: ## Run formatters & linters
	docker compose run --rm backend black --check .
	docker compose run --rm backend ruff .
	docker compose run --rm backend mypy .

unit: ## Run unit tests
	docker compose run --rm backend pytest -q backend/tests/unit

integration: ## Run integration tests
	docker compose run --rm backend pytest -q backend/tests/integration

coverage:
	docker compose run --rm backend pytest --cov=backend --cov-report=xml

serve:
	docker compose up backend
```
