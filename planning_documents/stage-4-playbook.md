# Stage 4 · Integration & Testing Playbook (Updated 2025-07-12)

> **This playbook is updated to reflect all standards, workflows, and lessons learned from Stages 1–3.**
> 
> - **All integration, E2E, and verification tasks must be run in Docker or CI.**
> - **All contributors must read and follow the planning documents and onboarding sections in the README before making changes.**
> - **All dependencies, scripts, and tool versions are strictly pinned and must match `versions.md`.**
> - **All quality gates (lint, format, type, test, coverage) must pass in Docker and CI before any integration or E2E testing.**
> - **Troubleshooting and cross-platform tips are included throughout.**

---
## 1 · Context and Dependencies

### 1.1 Incoming Deliverables
* Frozen **OpenAPI 3.1** spec from backend build.
* Generated TypeScript clients and React hooks (`openapi-typescript-codegen`).
* Frontend “Generate Slides” flow, mocked download component, and ≥ 90 % unit coverage.
* **All code, tests, and scripts must pass in Docker and CI before integration begins.**
* **All dependencies and tool versions must be pinned in `versions.md`.**

### 1.2 Exit Criteria
* All contracts verified and published to Pact Broker with **0 unverified** interactions.
* Cypress suite proves the *prompt → PPTX* journey in Chrome & Firefox with **≥ 95 %** reliability across three parallel CI runners.
* k6 thresholds: `http_req_failed < 1 %`, `http_req_duration p(95) < 400 ms`, peak 150 VU sustained 5 min with ≤ 2 % error.
* ZAP baseline **and** authenticated API scans report **no high/critical alerts**.
* Lighthouse budgets pass on every PR: total JS ≤ 250 KB, TTI ≤ 3 s (mobile), CLS ≤ 0.1.
* **All integration and E2E jobs must pass in CI (GitHub Actions) before merge.**
* **All contributors have read and followed onboarding and planning docs.**

---
## 2 · Work Breakdown Structure

| ID | Task | Key Inputs | Duration (h) | Outputs |
|----|------|------------|--------------|---------|
| 4-1 | Contract test harness | OpenAPI spec, Pact CLI | 6 | Pact setup scripts |
| 4-2 | Provider verification CI | FastAPI app, `pact-provider-verifier` | 4 | GH Action job publishes status |
| 4-3 | Cypress flow scaffolding | Phase 3 UI, `cypress-downloadfile` | 8 | `/e2e/prompt-pptx.cy.ts` |
| 4-4 | Download validation | S3 presign, file checksum | 5 | Binary integrity assertion |
| 4-5 | Lighthouse budgets + CI action | `budget.json`, `treosh/lighthouse-ci-action` | 4 | Failing status on regression |
| 4-6 | k6 smoke script | 10 VU, 1 min | 3 | `smoke.js`, pipeline gate |
| 4-7 | k6 load & stress | stages array, thresholds | 8 | `load.js`, `stress.js`, HTML reports |
| 4-8 | ZAP baseline scan | `zaproxy/action-baseline` | 4 | HTML/MD security report |
| 4-9 | ZAP authenticated API scan | `zap-api-scan.py`, JWT replacer | 6 | Auth scan HTML report |
| 4-10 | Exit review & sign-off | All reports | 2 | Sign-off minutes |

**Critical path:** 4-1 → 4-2 → 4-3 → 4-4 → 4-7 → 4-9 → 4-10

---
## 3 · Engineering Execution Details

### 3.1 Monorepo, Docker, and CI Enforcement
- **Monorepo structure:** All integration and E2E code must reside in the appropriate `frontend/`, `backend/`, or `.github/` directories. See `architecture-overview.md`.
- **All scripts, tests, and quality gates must be run in Docker or CI.**
- **All tool versions (Cypress, k6, ZAP, Lighthouse CI, Pact, etc.) must match `versions.md` and be run via Docker or CI.**
- **Backend quality checks:** Use Makefile targets or Docker Compose commands as documented in `backend-README.md` and `stage-1-foundation.md`.
- **Frontend quality checks:** Use npm scripts in Docker as documented in `README.md` and `stage-1-foundation.md`.
- **Troubleshooting (Windows):** Always delete `node_modules` and reinstall in Docker when switching between host and container to avoid native module issues. Ensure all cache and coverage directories are writable in Docker.

### 3.2 Contract Testing
1. **Consumer side**  
   • Wrap TanStack Query calls in Pact `setup()`; generate interactions for `/chat/generate`, `/slides/download`.  
   • Publish pacts to hosted broker (`CI_PACT_URL`).
2. **Provider side**  
   • Add `pact-verifier` stage in backend GitHub Actions referencing broker tags `main && prod`.  
   • Use FastAPI dependency overrides to establish data fixtures before each verification run.

### 3.3 Cypress End-to-End Suite
* **File download** – integrate `cypress-downloadfile` to pull the presigned PPTX and save under `cypress/downloads/`, then assert existence.  
* **Network interception** – stub `/chat/generate` via `cy.intercept` until provider verification passes, then switch to live endpoint.  
* **Accessibility check** – run `cypress-axe` in the same flow to maintain WCAG AA.

CI matrix: `browser=[chrome,firefox]`, `ui=desktop,mobile`.

### 3.4 k6 Performance Scripts
* **Smoke (`smoke.js`)** – 10 VU, 60 s, exit if `http_req_failed > 0`.
* **Load (`load.js`)** – stages: `[{d:'2m',t:20},{d:'5m',t:150},{d:'2m',t:0}]`.
* Add thresholds inside `options` per best practice and output InfluxDB line protocol for Grafana.
* Execute via Docker image `grafana/k6:latest` in self-hosted runner to avoid limits.

### 3.5 OWASP ZAP Scans
* **Baseline** – `zaproxy/action-baseline@v0.10.0` against `https://staging.ai-ppt.io`, upload HTML artefact.  
* **Authenticated API** – use:
  ```bash
  zap-api-scan.py -t openapi.json -f openapi \
    -z "-config replacer.full_list(0).matchstr=Authorization \
        -config replacer.full_list(0).replacement=Bearer $CI_JWT"
  ```
* Keep scans in safe-mode (no active attack) for CI; enable full active scan manually before release.

### 3.6 Lighthouse Budgets
* Add `budget.json` at repo root (document, script, total budgets).
* Run `treosh/lighthouse-ci-action` on PRs; fail build if any assertion fails, publish HTML report as artefact.
* Adopt **LightWallet** metrics for resource counts.

---
## 4 · CI/CD Wiring

### 4.1 GitHub Actions Jobs
1. `contracts` – run consumer tests → upload pact.  
2. `provider-verify` – depends on backend build; fetch pact, verify, publish result.  
3. `e2e` – build frontend image → Cypress Docker action → upload video/screenshots.  
4. `perf-smoke` – parallel job; gate before merge to `main`.  
5. `security-zap` – nightly schedule plus on-demand dispatch.  
6. `lhci` – on every push, uses Lighthouse CI action with budgets.

### 4.2 Fail-Fast Strategy
* Any red budget or failed threshold **blocks merge**.  
* ZAP Warn-only alerts are tolerated; Fail-level alerts fail pipeline by passing `fail_action: true`.
* **All reports and artifacts are published as CI artifacts.**

---
## 5 · Risk Register & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Contract drift between spec & provider | E2E flakiness | Nightly pact verification; spec freeze gate |
| Large PPTX ➜ slow download | User churn | k6 checks file transfer time; adjust chunk size |
| ZAP auth token expiry | False positives | CI step regenerates JWT every run |
| Lighthouse noise on CI hardware | Budget churn | Use throttled device emulation & median of 3 runs |
| Platform-specific test failures (esp. Windows) | CI flakiness | Enforce Docker/CI for all checks; see troubleshooting in README |

---
## 6 · Success Checklist

- [ ] **All Pact interactions verified** in broker dashboard.  
- [ ] **Cypress suite green** across browsers, 0 flaky retries for two consecutive runs.  
- [ ] **k6 load test passes** thresholds at 150 VU.  
- [ ] **ZAP reports 0 high alerts**; medium issues triaged.  
- [ ] **Lighthouse budgets** all green with diff comment posted on PR.
- [ ] **All contributors have read and followed onboarding and planning docs.**

---
## 7 · Lessons Learned from Foundation Setup (2025-07-12)
- **Strict version pinning** (see `versions.md`) is essential for reproducibility and cross-platform reliability.
- **All development, testing, and quality checks must be run in Docker or CI** to avoid platform-specific issues (especially on Windows).
- **All contributors must read onboarding and planning docs before making changes.**
- **Troubleshooting:** Always delete `node_modules` and reinstall in Docker when switching between host and container. Ensure all cache and coverage directories are writable in Docker. See `README.md` and `stage-1-foundation.md` for more tips.
- **All code, tests, and scripts must pass in Docker and CI before integration begins.**

---

With this playbook, the team can execute **Phase 4** efficiently, ensuring functional correctness, performance resilience, and security hardening before final deployment.

**Document version:** 2.0  
**Last Updated:** 2025-07-12
