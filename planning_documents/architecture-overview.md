# AI-PowerPoint-Generator: Modern React 18 + TypeScript Architecture (Revised 2025-07-12)

> This document supersedes the earlier *architecture-overview.md*. It applies all corrections highlighted in the Inconsistency Audit and is now the single source of truth.
>
> • **All version numbers** are strictly enforced via `versions.md` and Docker/CI (Node.js 18.19.0, Python 3.12.0, Vite 5.1.4, @vitejs/plugin-react 4.2.0, etc.).  
> • **All development, testing, and quality checks must be run in Docker or CI for cross-platform reliability.**  
> • **Directory conventions** are finalised (backend entry-point `backend/app/main.py`).  
> • **Real-time stack** now uses *python-socketio* exclusively (no Flask layer).  
> • **Persistence layer** is deferred; no PostgreSQL/SQLAlchemy references remain.  
> • **Performance targets** align with Stage 5 SLO (API P95 ≤ 400 ms in production).

---

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (React 18 + TypeScript)"
        A[Vite 5 + React Plugin] --> B[React 18 Components]
        B --> C[TanStack Router v1 (manual composition)]
        B --> D[Zustand v4.5 State]
        B --> E[TanStack Query v5]
        B --> F[shadcn/ui]
        B --> G[Framer Motion]
        E --> H[Socket.IO 4 Client]
    end

    subgraph "Backend (Python FastAPI)"
        I[FastAPI 0.111 + Uvicorn]
        J[Pydantic v2 Models]
        K[OpenRouter LLM Service]
        L[Runware Image Service]
        M[python-pptx Deck Builder]
        N[python-socketio 5 Server]
    end

    subgraph "Type Safety Pipeline"
        O[OpenAPI Schema]
        P[openapi-typescript-codegen]
        Q[Generated TS Types]
    end

    H <--> N
    E <--> I
    O --> P
    P --> Q
    Q --> E
    I --> J
    I --> K
    I --> L
    I --> M
```

### Change Log vs. Previous Version
| Section | Previous | Revised |
|---------|----------|---------|
| **State Manager** | Zustand v5 | Zustand v4.5  → matches NPM lockfile |
| **Forms Library** | react-hook-form v8 | react-hook-form v7.49 |
| **stylelint** | 15.x | 16.1  → matches frontend README |
| **Real-time Bridge** | Flask-SocketIO + python-socketio mix | Single *python-socketio* server |
| **Database** | PostgreSQL/SQLAlchemy mentioned implicitly | All persistence references removed (no DB in Phase 1–4) |
| **Performance Budget** | API P95 ≤ 800 ms | API P95 ≤ 400 ms (prod); ≤ 600 ms (staging) |
| **Frontend Build** | Vite 7.x, plugin-react 4.6.x | Vite 5.1.4, @vitejs/plugin-react 4.2.0 (strictly pinned) |
| **Routing Plugin** | Router Vite plugin enabled | Router Vite plugin removed; manual route-tree composition |
| **Testing** | Jest/Vitest mix | Vitest + React Testing Library only, all tests run in Docker |
| **CI/CD** | Not enforced | GitHub Actions for lint, test, coverage; all contributors must use Docker/CI |

### Technology Stack (Versions in `versions.md`)

The table of exact versions has been removed from this file to avoid drift. **Consult `versions.md`** for the canonical matrix. All contributors must use only pinned versions from that file.

---

## Development Workflow (Updated)

1. **Type Safety Pipeline** – unchanged, but the nightly regeneration job is now defined in `.github/workflows/type-sync.yml`.
2. **Real-time Communication** – frontend Socket.IO v4 client connects directly to `python-socketio` ASGI app mounted at `/ws` (see backend README).
3. **Persistence** – deferred; services remain stateless in Phases 1–4.
4. **Testing Targets** – backend and frontend unit coverage ≥ 90 %, E2E coverage gated in Stage 4.
5. **All development, testing, and quality checks must be run in Docker or CI for cross-platform reliability.**
6. **All contributors must read the planning documents and onboarding sections in the README before making changes.**

---

## Security & Performance Targets (Aligned)

| Metric | Target | Tool | Stage |
|--------|--------|------|-------|
| API latency P95 | ≤ 400 ms (prod) / ≤ 600 ms (staging) | k6, Prometheus | 5 |
| Slide generation turnaround | ≤ 30 s (5-slide deck) | k6 | 4 |
| Lighthouse Performance | ≥ 90 | CI LHCI | 3 |
| Unit test coverage | ≥ 90 % lines + branches | Coverage.py / Vitest | 2 & 3 |

---

## Directory Conventions (Final)
```
backend/
└── app/
    ├── main.py          # FastAPI entry-point
    ├── api/
    ├── models/
    ├── services/
    └── socketio_app.py  # python-socketio instance
```
All tooling (Makefile, Dockerfiles, CI commands) point to `backend/app/main.py`.

---

## Stage 1 Foundation: Summary & Lessons Learned (2025-07-12)
- **Dockerfiles and docker-compose** for both frontend and backend are complete and verified.
- **All dependencies are strictly pinned and enforced via versions.md, Docker, and CI.**
- **CI/CD (GitHub Actions)** is live for lint, test, and coverage on all PRs and pushes.
- **All code is auto-formatted and passes all quality gates in Docker and CI.**
- **README and planning documents** are updated for onboarding and compliance.
- **All contributors must use Docker and CI workflows for all quality checks and development.**

### Troubleshooting & Cross-Platform Tips
- Always delete `node_modules` and reinstall in Docker when switching between host and container to avoid native module issues (especially on Windows).
- Ensure all cache and coverage directories are writable in Docker for local runs.
- Use only pinned dependency versions from `versions.md`.
- All quality checks must be run in Docker or CI for consistency.

---

## Deprecations

1. **Flask-SocketIO** – fully removed; `python-socketio 5` satisfies server requirements.  
2. **SQLAlchemy/Alembic** – removed from Phase 1–3; will be revisited only when a persistence feature enters the backlog.

---

## Future Enhancements (Unchanged)
- Collaborative editing, template marketplace, plugin system, etc.

---

**Document Version:** 2.1  
**Effective Date:** 2025-07-12  
**Next Review:** 2025-07-23

---

## Change Log
| Date | Change | Author |
|------|--------|--------|
| 2025-07-20 | Stage 2 backend complete: Backend stack finalized (FastAPI, Pydantic v2, python-socketio, OpenRouter, Runware, strict type/coverage gates, Bandit, Trivy, contract tests, k6). | AI Assistant |