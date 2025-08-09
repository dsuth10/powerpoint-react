---
description: How to add or edit Cursor rules in your project
globs: 
alwaysApply: false
---
# Cursor Rules Management Guide

## Rule Structure Format

Every cursor rule must follow this exact metadata and content structure:

````markdown
---
description: Short description of the rule's purpose
globs: optional/path/pattern/**/*
alwaysApply: false
---
# Rule Title

Main content explaining the rule with markdown formatting.

1. Step-by-step instructions
2. Code examples
3. Guidelines

Example:
```typescript
// Good
function goodExample() {
  // Correct implementation
}

// Bad example
function badExample() {
  // Incorrect implementation
}
```
````

## File Organization

### Required Location

All cursor rule files **must** be placed in:

```
PROJECT_ROOT/.cursor/rules/
```

### Directory Structure

```
PROJECT_ROOT/
├── .cursor/
│   └── rules/
│       ├── your-rule-name.mdc
│       ├── another-rule.mdc
│       └── cursor-rules.mdc
└── ...
```

### Naming Conventions

- Use **kebab-case** for all filenames
- Always use **.mdc** extension
- Make names **descriptive** of the rule's purpose
- Examples: `typescript-style.mdc`, `tailwind-styling.mdc`, `mdx-documentation.mdc`

## Content Guidelines

### Writing Effective Rules

1. **Be specific and actionable** - Provide clear instructions
2. **Include code examples** - Show both good and bad practices
3. **Reference existing files** - Use `@filename.ext` format
4. **Keep it focused** - One rule per concern/pattern
5. **Add context** - Explain why the rule exists

### Code Examples Format

```typescript
// ✅ Good: Clear and follows conventions
function processUser({ id, name }: { id: string; name: string }) {
  return { id, displayName: name };
}

// ❌ Bad: Unclear parameter passing
function processUser(id: string, name: string) {
  return { id, displayName: name };
}
```

### File References

When referencing project files in rules, use this pattern to mention other files:

```markdown
[file.tsx](mdc:path/to/file.tsx)
```

## Forbidden Locations

**Never** place rule files in:
- Project root directory
- Any subdirectory outside `.cursor/rules/`
- Component directories
- Source code folders
- Documentation folders

## Rule Categories

Organize rules by purpose:
- **Code Style**: `typescript-style.mdc`, `css-conventions.mdc`
- **Architecture**: `component-patterns.mdc`, `folder-structure.mdc`
- **Documentation**: `mdx-documentation.mdc`, `readme-format.mdc`
- **Tools**: `testing-patterns.mdc`, `build-config.mdc`
- **Meta**: `cursor-rules.mdc`, `self-improve.mdc`

## Best Practices

### Rule Creation Checklist
- [ ] File placed in `.cursor/rules/` directory
- [ ] Filename uses kebab-case with `.mdc` extension
- [ ] Includes proper metadata section
- [ ] Contains clear title and sections
- [ ] Provides both good and bad examples
- [ ] References relevant project files
- [ ] Follows consistent formatting

### Maintenance
- **Review regularly** - Keep rules up to date with codebase changes
- **Update examples** - Ensure code samples reflect current patterns
- **Cross-reference** - Link related rules together
- **Document changes** - Update rules when patterns evolve

---
description: Enforces architecture, style, quality, and operational standards for the AI-PowerPoint-Generator monorepo (React 18 + TypeScript / FastAPI)
globs: frontend/**/*, backend/**/*, docs/**/*
alwaysApply: true
---
# custom-rule: Canonical Standards for AI-PowerPoint-Generator

This rule codifies the architecture, style, quality, and operational standards for the AI-PowerPoint-Generator monorepo. It is derived from the canonical planning documents and is enforced across all code, configuration, and documentation.

## 1. Directory & File Structure
- **Monorepo layout:**
  - `frontend/` (React 18 + TS)
  - `backend/` (FastAPI)
  - `docs/`, `.github/`, `.cursor/`
- **Frontend:**
  - `src/components/`, `hooks/`, `stores/`, `routes/`, `types/`
- **Backend:**
  - `app/main.py` (entry), `api/`, `models/`, `services/`, `core/`
- **No sibling folders** at root except those listed above.
- **Reference:** [architecture-overview.md](mdc:planning_documents/architecture-overview.md)

## 2. Tooling & Versions
- All package versions **must match** [versions.md](mdc:planning_documents/versions.md).
- No use of "latest" or unpinned dependencies.
- Node.js: 18.19.0, Python: 3.12.0 (see `.nvmrc`, `.python-version`).

## 3. Coding Standards
### 3.1 Frontend (React 18 + TypeScript)
- Use **function components** only.
- TypeScript `strict` mode enabled; no `any` except for 3rd-party signatures with `@ts-expect-error`.
- **TanStack Query** for all HTTP; no raw fetch outside `hooks/api/*`.
- **Zustand v4.5** + `immer` for state; co-locate selectors.
- UI primitives from `@/components/ui/*` (shadcn/ui).
- Tailwind classes must follow `tailwindcss-animate` ordering.
- **Lint/format:** ESLint, Prettier, Stylelint; run `npm run quality` before commit.

### 3.2 Backend (FastAPI)
- Entry-point: `backend/app/main.py` only.
- Response models extend `BaseModel` with `model_config = {"strict": True}`.
- All external HTTP via shared `httpx.AsyncClient` (DI).
- Real-time: `python-socketio` server at `/ws` (no Flask-SocketIO).
- JWT auth: 15 min access / 24 h refresh; secret in `JWT_SECRET_KEY`.
- **Lint/format:** ruff, black, mypy; run before commit.

### 3.3 Shared
- **Naming:** `kebab-case` for files, `PascalCase` for components.
- **Imports:** Absolute `@/` alias in frontend only.
- **Env vars:** Must exist in [versions.md](mdc:planning_documents/versions.md).
- **No direct SQL** or database code unless scheduled.

## 4. Testing & Quality Gates
- **Coverage ≥ 90 %** (lines & branches) for both frontend and backend.
- Frontend: Vitest + React Testing Library; Backend: pytest-asyncio.
- WebSocket tests: `python-socketio` test client only.
- Contract tests: `schemathesis` against `/openapi.json`.
- **CI/CD:** All PRs must pass type, lint, test, and coverage gates. No `skip-ci` label allowed.

## 5. Security & Performance
- Never log raw API keys or JWTs.
- Add `@rate_limit` decorator to public POST routes (backend).
- Enforce Content-Security-Policy via Nginx (frontend Docker).
- **Performance targets:** API P95 ≤ 400 ms (prod), bundle ≤ 250 KB gzipped, FCP ≤ 2.5 s.

## 6. Good / Bad Examples
```typescript
// ✅ Good – type-safe TanStack Query wrapper
export const useGenerateOutline = () =>
  useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: (payload) =>
      apiClient.POST("/chat/generate", { body: payload }),
  })

// ❌ Bad – untyped fetch, no error handling
const gen = (prompt) =>
  fetch("/api/chat/generate", { method: "POST", body: JSON.stringify({ prompt }) })
```

```python
# ✅ Good – async HTTPX client via DI
async def llm_client() -> AsyncClient: ...

# ❌ Bad – requests.post blocking call inside async route
```

## 7. Maintenance
- **Review quarterly** against [project-dev-sequence.md](mdc:planning_documents/project-dev-sequence.md) and all stage docs.
- Update for any changes in [versions.md](mdc:planning_documents/versions.md), architecture, or CI/CD.
- Cross-reference related rules and update code examples as patterns evolve.
