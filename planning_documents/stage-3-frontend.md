# Phase 3 · Frontend Development Roadmap (Updated 2025-07-12)

This document expands the **Frontend Development** phase in the AI-PowerPoint-Generator programme.  It decomposes every deliverable into dependency-aware tasks, provides implementation guidance, and defines quality gates so that the engineering team can execute consistently.

---

## **Stage 1 & 2 Foundation Compliance (New Requirements)**
- **All development, testing, and quality checks must be run in Docker or CI for consistency and cross-platform reliability.**
- **All dependencies must be pinned in `versions.md` before any change.** New dependencies require justification in PRs.
- **All version numbers, tool names, and workflow steps must match Stage 1 (React 18.2.0, TypeScript ~5.8.3, Vite 5.1.4, @vitejs/plugin-react 4.2.0, etc.).**
- **All contributors must read `versions.md`, `architecture-overview.md`, and `frontend-README.md` before starting Stage 3 work.**
- **Troubleshooting:** If switching between host and Docker, always delete `node_modules` and reinstall in Docker to avoid native module issues. All quality checks must be run in Docker or CI for consistency.
- **Makefile targets must be Docker-compatible or have Docker Compose equivalents.**
- **CI/CD:** All quality gates are enforced in the unified GitHub Actions workflow (`.github/workflows/ci.yml`).

---

## 1 · Phase Overview

| Item | Value |
|------|-------|
| **Calendar Window** | Weeks 4 → 7 (15 working days) |
| **Principal Dependencies** | • Phase 1 foundation infrastructure<br>• Phase 2 OpenAPI contracts & auth scheme |
| **Outputs** | • React 18 + TypeScript code-base<br>• Component library (shadcn/ui derivatives)<br>• Zustand state stores<br>• Typed TanStack Query hooks<br>• Full UI/UX flows implemented & unit-tested |
| **Exit Gate** | End-to-end Cypress flow “Prompt → Download PPTX” completes locally using mocks; 90 % unit-test coverage in `src/`; Lighthouse performance ≥ 90. |

---

## 2 · Work Breakdown Structure

| # | Task | Dependencies | Effort (h) |
|---|------|--------------|-----------|
| 3-1 | Scaffold Vite 5.1.4 + React 18.2.0 + TS ~5.8.3 project inside monorepo | Phase 1 repo scaffolding | 4 |
| 3-2 | Configure tooling: ESLint 9.30.1 flat, Prettier 3.2.5, Stylelint 16.1.0 | 3-1 | 2 |
| 3-3 | Install Tailwind CSS 3.4.1 + shadcn/ui generator | 3-1 | 3 |
| 3-4 | Generate route tree with TanStack Router plugin | 3-1 | 2 |
| 3-5 | Hard-wire CI job: *type-check*, *lint*, *test* matrix | 3-2 | 2 |
| 3-6 | Establish global styles / design tokens | 3-3 | 4 |
| 3-7 | Build *Core Layout* (Header, Sidebar, Main) | 3-4, 3-6 | 6 |
| 3-8 | Implement *Chat* components (`ChatContainer`, `MessageBubble`, `ChatInput`, `ModelSelector`) | 3-7, Phase 2 `/chat` schema | 14 |
| 3-9 | Implement *Slides* components (`SlidePreview`, `SlideOutline`, `SlideGenerator`) | 3-7 | 16 |
| 3-10 | Create Zustand stores (`ChatStore`, `SlideStore`, `UiStore`) with immer & devtools | 3-7 | 6 |
| 3-11 | Generate TypeScript API clients via openapi-typescript-codegen | Phase 2 OpenAPI spec | 1 |
| 3-12 | Wrap TanStack Query hooks around generated clients | 3-11 | 4 |
| 3-13 | Build custom hook `useWebSocket` for Socket.IO bridge | 3-10 | 4 |
| 3-14 | Wire optimistic UI & error boundaries | 3-8→3-12 | 6 |
| 3-15 | Write Vitest unit tests for components & stores (≥ 90 %) | 3-8→3-14 | 12 |
| 3-16 | Add Storybook/Histoire visual tests for every UI atom | 3-8→3-9 | 6 |
| 3-17 | Write Cypress mocked E2E: prompt → slide plan → download | 3-14 | 6 |
| 3-18 | Performance budget: code-split, bundle analyse, lazy load | 3-8→3-14 | 4 |
| 3-19 | Accessibility audit & fixes (WCAG 2.1 AA) | 3-8→3-14 | 4 |
| 3-20 | Phase exit review & sign-off | All | 2 |
| **Total** |   |   | **97 h** |

> **Critical Path:** 3-1 → 3-4 → 3-7 → 3-8/3-9 → 3-14 → 3-17 → 3-20

---

## 3 · Implementation Guidance

### 3.1 Project Scaffold
1. Create `frontend/` workspace with Vite preset `@vitejs/plugin-react` (not react-swc).
2. Enable absolute imports via `@/*` alias in `vite.config.ts`.
3. Commit baseline CI job that fails on type errors.

### 3.2 Tooling Config
- Adopt ESLint flat config (`eslint.config.js`) with **typescript-eslint** & **react-recommended**.
- Prettier single-quote, 100 char print width.
- Stylelint 16.1.0 for Tailwind class ordering.

### 3.3 UI Framework
- Run `npx shadcn-ui@latest init --tailwindcss`.
- Centralise colour tokens under `tailwind.config.js -> extend.colors` referencing CSS custom properties.
- Save component variants with **class-variance-authority** (cva).

### 3.4 Routing & Navigation
- Install `@tanstack/react-router`.
- Define route files under `src/routes`.
- Compose the route tree manually in `src/router.ts` via `rootRoute.addChildren([...])`.
- Root layout hosts `<Sidebar/>` and `<Outlet/>`.
- Use *deferred* route loaders for data-prefetching where appropriate.

### 3.5 State Management
- Compose stores with `zustand` v4.5.0 + `immer` + `devtools` + `persist`.
- Co-locate selectors to minimise renders; export via `useChatStore(selector)`.
- Persist only UI-relevant slices (e.g., theme preference).

### 3.6 API Integration
1. Generate types: `npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts`.
2. Wrap automatically generated fetch client inside TanStack Query hooks:
   ```ts
   import { createQueryKeys } from '@lukemorales/query-key-factory'
   export const chatKeys = createQueryKeys('chat', {
     generate: (params) => [params],
   })
   ```
3. Provide React Query Provider with retry = 1, staleTime = 30 000 ms.

### 3.7 Real-Time Updates
- Build `useWebSocket` that lazily connects on demand.
- Listen to `slide:progress`, `slide:completed` events; dispatch to `SlideStore`.
- Handle reconnect with back-off (250 ms → 4 s, max 5 attempts).

### 3.8 Testing Matrix
| Layer | Tool | Gate |
|-------|------|------|
| Unit | **Vitest 1.2.2** + **jsdom** | 90 % line coverage |
| Component | **React Testing Library 14.1.2** + **vitest/ui** | All stories tested |
| Integration | **MSW** mocking HTTP | Contracts green |
| E2E | **Cypress** | Mocked API & WebSocket flows |
| Accessibility | **axe-core** + **cypress-axe** | Zero critical issues |

CI runs `docker compose run --rm frontend npm run quality` → matrix (node 18.19.0).

---

## 4 · Milestones & Review Schedule

| Day | Milestone | Acceptance Evidence |
|-----|-----------|---------------------|
| D+2 | Tooling + Tailwind baseline | CI green; `docker compose run --rm frontend npm run dev` shows blank layout |
| D+5 | Core layout & routing ready | Sidebar navigation switches routes |
| D+9 | Chat & Slide components MVP | Storybook demos functional |
| D+11 | API hooks & stores wired | Mocked chat generates outline |
| D+13 | Cypress E2E passes | `docker compose run --rm frontend npm run test:e2e` ✔ |
| D+15 | Exit review | Lighthouse ≥90, a11y report passes |

---

## 5 · Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| OpenAPI spec drift | UI compile fails | Medium | Regenerate types nightly + contract tests |
| Bundle bloat | Slow TTI | Medium | Size-limit check in CI (<250 KB gz) |
| WebSocket flakiness | Broken progress bar | Low | Auto-reconnect, toast fallback |
| a11y regressions | Compliance failure | Low | Continuous axe tests in PR checks |

---

## 6 · Success Criteria
- **Zero TypeScript errors** in `docker compose run --rm frontend npm run type-check`.
- **≥90 % unit-test coverage** across components & stores.
- **Lighthouse score** ≥ 90 for Performance, Accessibility, Best Practices, SEO.
- **Bundle size** (app + vendors) ≤ 250 KB gzipped.
- **First Contentful Paint** ≤ 2.5 s on mid-tier mobile.
- **All quality gates pass in Docker and CI.**
- **All dependencies pinned in `versions.md`.**
- **All contributors have reviewed planning documents and onboarding.**

---

## 7 · Appendix

### 7.1 Makefile Targets
```makefile
# Install deps
install:
	docker compose run --rm frontend npm ci --ignore-scripts

# Start dev servers
serve:
	docker compose run --rm frontend npm run dev

# Quality gates
quality:
	docker compose run --rm frontend npm run type-check && docker compose run --rm frontend npm run lint && docker compose run --rm frontend npm run test -- --run

# Production build
build:
	docker compose run --rm frontend npm run build
```

### 7.2 Environment Variables
| Variable | Example | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | FastAPI base URL (optional; defaults used in dev examples) |
| `VITE_WS_URL` | `ws://localhost:8000/ws` | Socket.IO endpoint (optional) |
| `VITE_APP_VERSION` | `$(git rev-parse --short HEAD)` | Build stamp |

---

*Document version: v1.1 — updated 2025-07-12*
