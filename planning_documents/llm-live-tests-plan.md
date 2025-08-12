## Backend LLM Testing Plan (Live + Mocked)

### Overview
This document defines a comprehensive test strategy for exercising the backend LLM service with both fast, deterministic mocked tests and opt-in live integration tests against OpenRouter using secrets from the `backend/.env` file. It aligns with existing patterns, markers, and coverage gates in this repository.

### Goals
- Ensure robust coverage of happy paths, error handling, model selection, and fallback logic for `app/services/llm.py`.
- Provide reliable, quick default test runs via mocks while enabling explicit live runs that hit the real APIs.
- Integrate cleanly with current `pytest` markers, configuration, and repository standards.

### Current State (as of this plan)
- **Configuration**: `app/core/config.py` reads `.env` with `pydantic-settings`.
  - Key fields: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_DEFAULT_MODEL`, `OPENROUTER_ALLOWED_MODELS`, `OPENROUTER_TIMEOUT_SECONDS`, `LLM_LOG_PROMPTS`.
- **Service**: `app/services/llm.py`.
  - Primary path: POST `/{base}/chat/completions`; parse JSON embedded in `choices[0].message.content`.
  - Fallback path: POST `/{base}/generate` (legacy shape) if primary throws.
  - Offline fallback if no API key set.
- **Models**: `app/models/chat.py` (`ChatRequest`, `ChatResponse`).
- **Tests/markers**: see `backend/pytest.ini` and existing tests like [test_llm_service.py](mdc:backend/tests/test_llm_service.py). Markers include `live` and `live_llm`.

### Strategy
- **Unit-like (mocked via respx) — default**
  - Mock upstream endpoints to exercise payload shape, parsing, retries, rate limits, and fallbacks. These run in every `pytest` invocation and meet the coverage gate.
- **Live integration (opt-in) — explicit**
  - Real calls to OpenRouter when `RUN_LIVE_LLM=1` and `OPENROUTER_API_KEY` exist. Keep inputs small to control cost and runtime.

### Environment & Secrets
- Place `.env` in `backend/` with at minimum:
  - `OPENROUTER_API_KEY=<your-key>`
  - `OPENROUTER_DEFAULT_MODEL=openrouter/gpt-4o-mini`
  - `OPENROUTER_ALLOWED_MODELS=["openrouter/gpt-4o-mini","openrouter/gpt-4o"]` (JSON array recommended)
  - `LLM_LOG_PROMPTS=false`
- Live tests require: `RUN_LIVE_LLM=1` in environment.
- Reference versions in [versions.md](mdc:planning_documents/versions.md) before changing dependencies.

### Test Cases to Cover
- **Model allowlist enforcement**
  - Requesting a model not in `OPENROUTER_ALLOWED_MODELS` raises an error.
- **Primary path JSON parsing**
  - `/chat/completions` response contains `message.content` with trailing JSON. Verify `ChatResponse` is constructed with valid `SlidePlan`s.
- **Malformed content + fallback**
  - `/chat/completions` returns content without JSON → raise malformed error → fallback to `/generate` succeeds.
- **Retry on transient error (fast)**
  - First `/chat/completions` = 500, second = 200. Assert call count indicates one retry; avoid long sleeps.
- **Rate limit handling**
  - `/chat/completions` returns `429` with `Retry-After`. Verify error includes header value. Optionally mirror on `/generate`.
- **Offline mode**
  - Unset `OPENROUTER_API_KEY` and assert local outline returned with requested `slide_count`.
- **Live service-level call (opt-in)**
  - When enabled, call `generate_outline` with `slide_count=2`, `model=openrouter/gpt-4o-mini`. Assert two slides, each with `title` and list `bullets`.
- **Live API route (optional, opt-in)**
  - Use FastAPI `TestClient` to `POST /api/v1/chat/generate` with `{"prompt":"...","numSlides":2,"language":"en"}` ensuring HTTP mocking disabled. Assert two slide objects.

### Fixtures & Helpers
- Add `backend/tests/conftest.py` helpers:
  - `def live_llm_enabled():` returns `True` when `RUN_LIVE_LLM=1` and `OPENROUTER_API_KEY` set; used for centralized gating.
  - `no_http_mocks` fixture that stops `respx` during live tests so real network calls occur.

### File Touchpoints
- Expand or add tests in:
  - `backend/tests/test_llm_service.py`
  - `backend/tests/test_api_routes.py` (optional live route test)
  - `backend/tests/conftest.py` (new) for live gating and `respx` control

### Execution
- Default fast run (mocked only):
```powershell
cd backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q
```

- Live LLM tests:
```powershell
cd backend
$env:RUN_LIVE_LLM="1"; $env:OPENROUTER_API_KEY="<your-key>"
pytest -m "live and live_llm" -q
```

### CI/CD
- Keep live tests excluded from standard CI; run in a separate manual/scheduled job with secrets.
- Example CI step:
  - Set `OPENROUTER_API_KEY` secret; run `pytest -m "live and live_llm" -k test_generate_outline_live_llm --maxfail=1`.
- Maintain 90%+ coverage using mocked tests; live tests do not need to count toward coverage.

### Risk & Cost Controls
- Use `slide_count=2` and `temperature=0.3` (already configured) for low variance and cost.
- Limit models under test to one default model per live run.
- Ensure `LLM_LOG_PROMPTS=false` to avoid leaking sensitive inputs.

### Documentation Updates
- Update `planning_documents/backend-README.md` with:
  - `.env` keys for OpenRouter
  - How to enable and run live tests
  - Note on costs and potential rate limits

### Optional Enhancements
- Live SLA check: assert elapsed time under a soft threshold (e.g., < 10s) to detect slowness.
- Skip guard: if `OPENROUTER_DEFAULT_MODEL` not in `OPENROUTER_ALLOWED_MODELS`, skip with a clear message.

### Recommended Defaults
- **Live scope**: One model, `slide_count=2`.
- **Route-level live test**: One gated test to validate FastAPI path end-to-end.
- **Fixtures**: Centralize live gating and `respx` disabling in `conftest.py`.


