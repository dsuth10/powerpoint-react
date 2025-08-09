# Contributing

Please review `planning_documents/` before changes to align with architecture and versions.

- Run commands inside Docker (see README).
- Follow pinned versions in `planning_documents/versions.md`.
- Frontend: React 18 + TS, TanStack Query/Router, Zustand; no raw fetch.
- Backend: FastAPI + Pydantic v2, strict models.
- Quality gates: lint, typecheck, tests (≥90% coverage) must pass.

## Dev quickstart
- Windows (PowerShell): `make up; ./scripts/smoke.ps1`
- macOS/Linux: `make up && sleep 5 && curl -f http://localhost:8000/api/v1/health`

Open PRs with concise descriptions and links to relevant planning docs.
