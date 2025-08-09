# Frontend Module Guide

Modern React 18 + TypeScript frontend for the AI-PowerPoint-Generator application.

## Quick Start

```bash
# (Recommended) Use Docker for all development, testing, and quality checks
# This ensures cross-platform reliability and matches CI/CD.
# See below for Docker usage instructions.

# (Optional) Local npm install for advanced users only
npm install

# Start development server (in Docker)
docker compose run --rm frontend npm run dev

# Run tests (in Docker)
docker compose run --rm frontend npm run test -- --run

# Lint (in Docker)
docker compose run --rm frontend npm run lint

# Build for production (in Docker)
docker compose run --rm frontend npm run build
```

> **All contributors must use Docker or CI for all quality checks and development.**

## Technology Stack

### Core Framework
- **React 18.2.0** - Component library with Concurrent Features
- **TypeScript ~5.8.3** - Static type checking and enhanced IDE support
- **Vite 5.1.4** - Next-generation frontend build tool
- **@vitejs/plugin-react 4.2.0** - React plugin for Vite

### Routing & Navigation
- **TanStack Router v1.15.0** - Type-safe routing
- Route tree is composed manually in `src/router.ts` from route files in `src/routes/*` (plugin removed)

### State Management
- **Zustand v4.5.0** - Lightweight state management with React 18 optimisations
- **Immer integration** - Immutable state updates with simple syntax

### Data Fetching
- **TanStack Query v5.17.0** - Powerful data synchronisation for React
- **Socket.IO Client v4.7.4** - Real-time bidirectional communication

### UI Components & Styling
- **shadcn/ui** - Copy-paste component library built on Radix primitives
- **Tailwind CSS v3.4.1** - Utility-first CSS framework with JIT engine
- **Tailwind CSS Animate** - Animation utilities
- **class-variance-authority** - CSS class variant management
- **clsx** - Conditional className utility

### Forms & Validation
- **react-hook-form v7.49.3** - Performant, flexible forms with easy validation
- **@hookform/resolvers** - Validation library resolvers
- **zod** - TypeScript-first schema validation

### Animations
- **Framer Motion v11.0.6** - Production-ready motion library for React
- **Auto-animations** - Smooth layout transitions

### Testing
- **Vitest 1.2.2** - Fast unit test framework powered by Vite
- **React Testing Library 14.1.2** - Simple and complete testing utilities
- **@testing-library/jest-dom 6.6.3** - Custom DOM matchers
- **@testing-library/user-event** - User interaction simulation
- **Cypress** - End-to-end testing framework

### Code Quality
- **ESLint 9.30.1** - JavaScript/TypeScript linting with flat config
- **Prettier 3.2.5** - Code formatting
- **stylelint 16.1.0** - CSS/SCSS linting
- **TypeScript ESLint** - TypeScript-specific linting rules

## Docker Usage for Frontend Development

All frontend development, testing, and quality checks must be run in Docker or CI for consistency and cross-platform reliability.

- **Build and run frontend in Docker:**
  ```sh
  docker compose up -d frontend
  ```
- **Run lint, test, and build in Docker:**
  ```sh
  docker compose run --rm frontend npm run lint
  docker compose run --rm frontend npm run test -- --run
  docker compose run --rm frontend npm run build
  ```

> **Troubleshooting (Windows):**
> - If you encounter errors with esbuild or native modules, always delete node_modules and reinstall in Docker.
> - Always use Docker for all quality checks to avoid platform-specific issues.

## CI / CD

The frontend participates in the unified `CI-CD` GitHub Actions workflow. Key steps:

| Step | Tool | Gate |
|------|------|------|
| Lint | `eslint`, `stylelint` | Zero errors |
| Type check | `tsc` | Zero errors |
| Test | `vitest`, `@testing-library/react` | Coverage ≥ 90 % |
| Build | Docker multi-stage | Non-root image ≤ 250 MB |
| Scan | `trivy` | No HIGH / CRITICAL CVEs |

All quality gates are enforced in CI. See `.github/workflows/ci.yml` for details.

## Stage 1 Foundation Completion

- Frontend is fully Dockerized and all quality gates pass in Docker and CI.
- All dependencies are pinned and enforced via `versions.md`.
- All code is auto-formatted and type-checked.
- Contributors must read the planning documents before making changes.
- See `architecture-overview.md` and `README.md` for system context and onboarding.

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-07-12 | Stage 1 foundation complete: Docker, CI/CD, all quality gates, dependency pinning, documentation, and onboarding updated. | AI Assistant |

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui base components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── chat/           # Chat interface components
│   │   ├── chat-container.tsx
│   │   ├── message-bubble.tsx
│   │   ├── chat-input.tsx
│   │   └── model-selector.tsx
│   ├── slides/         # Slide-related components
│   │   ├── slide-preview.tsx
│   │   ├── slide-outline.tsx
│   │   └── slide-generator.tsx
│   └── layout/         # Layout components
│       ├── header.tsx
│       ├── sidebar.tsx
│       └── main-layout.tsx
├── hooks/              # Custom React hooks
│   ├── api/           # Generated API hooks
│   │   ├── use-chat.ts
│   │   ├── use-slides.ts
│   │   └── index.ts
│   ├── use-websocket.ts
│   ├── use-local-storage.ts
│   └── use-debounce.ts
├── lib/               # Utility functions and configurations
│   ├── api.ts         # API client configuration
│   ├── utils.ts       # General utilities
│   ├── constants.ts   # Application constants
│   ├── websocket.ts   # Socket.IO client setup
│   └── types.ts       # Shared type definitions
├── routes/            # TanStack Router route definitions
│   ├── __root.tsx     # Root layout
│   ├── index.tsx      # Home page
│   ├── chat/          # Chat routes
│   │   ├── index.tsx
│   │   └── $sessionId.tsx
│   └── slides/        # Slide routes
│       ├── index.tsx
│       └── $slideId.tsx
├── stores/            # Zustand state stores
│   ├── chat-store.ts
│   ├── slide-store.ts
│   ├── ui-store.ts
│   └── index.ts
├── styles/            # Global styles and configuration
│   ├── globals.css    # Global CSS and Tailwind imports
│   └── components.css # Component-specific styles
├── types/             # TypeScript type definitions
│   ├── api.ts         # Generated API types
│   ├── chat.ts        # Chat-related types
│   ├── slides.ts      # Slide-related types
│   └── index.ts       # Type exports
└── main.tsx           # Application entry point
```

## Configuration Files

### Vite Configuration (`vite.config.ts`)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
})
```

### TypeScript Configuration (`tsconfig.json`)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Tailwind Configuration (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

## Key Libraries & Versions

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | `^18.2.0` | Core React library |
| `react-dom` | `^18.2.0` | React DOM renderer |
| `typescript` | `^5.3.0` | TypeScript compiler |
| `vite` | `^5.1.0` | Build tool and dev server |
| `@vitejs/plugin-react` | `^4.2.0` | React plugin with SWC |
| `@tanstack/router` | `^1.15.0` | Type-safe routing |
| `@tanstack/react-query` | `^5.17.0` | Data fetching and caching |
| `zustand` | `^4.5.0` | State management |
| `react-hook-form` | `^7.49.0` | Form management |
| `framer-motion` | `^11.0.0` | Animation library |
| `socket.io-client` | `^4.7.0` | WebSocket client |
| `tailwindcss` | `^3.4.0` | CSS framework |
| `vitest` | `^1.2.0` | Testing framework |
| `@testing-library/react` | `^14.1.0` | React testing utilities |
| `cypress` | `^13.6.0` | E2E testing |
| `eslint` | `^9.0.0` | Code linting |
| `prettier` | `^3.2.0` | Code formatting |
| `stylelint` | `^16.1.0` | CSS linting |

## Coding Conventions

### Component Structure
```typescript
// components/example-component.tsx
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ExampleComponentProps {
  title: string
  isActive?: boolean
  onAction?: (id: string) => void
}

export function ExampleComponent({ 
  title, 
  isActive = false, 
  onAction 
}: ExampleComponentProps) {
  const [state, setState] = useState('')

  useEffect(() => {
    // Effect logic
  }, [])

  return (
    <motion.div
      className={cn(
        'base-classes',
        isActive && 'active-classes'
      )}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <h2>{title}</h2>
    </motion.div>
  )
}
```

### Hook Pattern
```typescript
// hooks/use-example.ts
import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'

export function useExample(id: string) {
  const [loading, setLoading] = useState(false)

  const { data, error, isLoading } = useQuery({
    queryKey: ['example', id],
    queryFn: () => fetchExampleData(id),
    enabled: !!id,
  })

  const handleAction = useCallback((action: string) => {
    setLoading(true)
    // Handle action
    setLoading(false)
  }, [])

  return {
    data,
    error,
    isLoading: isLoading || loading,
    handleAction,
  }
}
```

### Store Pattern (Zustand)
```typescript
// stores/example-store.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

interface ExampleState {
  items: Item[]
  selectedId: string | null
  setItems: (items: Item[]) => void
  selectItem: (id: string) => void
}

export const useExampleStore = create<ExampleState>()(
  devtools(
    persist(
      immer((set) => ({
        items: [],
        selectedId: null,
        setItems: (items) =>
          set((state) => {
            state.items = items
          }),
        selectItem: (id) =>
          set((state) => {
            state.selectedId = id
          }),
      })),
      {
        name: 'example-store',
        partialize: (state) => ({ selectedId: state.selectedId }),
      }
    ),
    { name: 'ExampleStore' }
  )
)
```

## Lint & Format Commands

```bash
# Type checking
npm run type-check         # Check TypeScript types
npm run type-check:watch   # Watch mode type checking

# Linting
npm run lint               # Run ESLint
npm run lint:fix           # Fix ESLint issues
npm run lint:css           # Run stylelint
npm run lint:css:fix       # Fix CSS issues

# Formatting
npm run format             # Format with Prettier
npm run format:check       # Check formatting

# All quality checks
npm run quality            # Run all checks (types, lint, format)
```

## Testing Commands

```bash
# Unit tests
npm run test              # Run Vitest
npm run test:watch        # Watch mode
npm run test:coverage     # Generate coverage report
npm run test:ui           # Open Vitest UI

# Component tests
npm run test:components   # Test React components specifically

# E2E tests
npm run test:e2e          # Run Cypress tests
npm run test:e2e:open     # Open Cypress UI
npm run test:e2e:headed   # Run with browser UI
```

## Development Workflow

### 1. Component Development
1. Create component in appropriate directory
2. Write TypeScript interfaces for props
3. Implement component with proper error boundaries
4. Add unit tests with React Testing Library
5. Update Storybook stories (if applicable)

### 2. API Integration
1. Generate TypeScript types from OpenAPI schema
2. Create TanStack Query hooks for data fetching
3. Implement error handling and loading states
4. Add optimistic updates where appropriate
5. Test with MSW (Mock Service Worker)

### 3. State Management
1. Define state shape with TypeScript interfaces
2. Create Zustand store with immer middleware
3. Implement selectors for optimal re-renders
4. Add devtools integration for debugging
5. Consider persistence for relevant state

### 4. Routing
1. Create route files in the routes directory
2. Define route parameters and search params
3. Implement loading and error states
4. Add navigation guards if needed
5. Test route transitions

## Performance Best Practices

### Code Splitting
- Route-based code splitting with TanStack Router
- Component lazy loading with React.lazy
- Third-party library code splitting

### Bundle Optimisation
- Tree shaking with Vite's rollup
- Dynamic imports for heavy components
- Bundle analysis with vite-bundle-analyzer

### Runtime Performance
- React.memo for expensive components
- useMemo and useCallback for expensive calculations
- Zustand selectors for minimal re-renders
- Virtual scrolling for large lists

### Network Optimisation
- TanStack Query caching strategies
- Image optimisation with WebP and lazy loading
- HTTP/2 server push for critical resources

## Accessibility Guidelines

### WCAG 2.1 AA Compliance
- Semantic HTML structure
- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Colour contrast requirements

### Testing Accessibility
```bash
npm run test:a11y         # Run accessibility tests
npm run test:a11y:audit   # Generate accessibility audit
```

## Browser Support

### Target Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Polyfills
- Core-js for older JavaScript features
- React 18 automatic runtime
- CSS custom properties fallbacks

## Troubleshooting

### Common Issues

#### Type Errors
```bash
# Clear TypeScript cache
rm -rf node_modules/.cache/typescript
npm run type-check
```

#### Build Issues
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run build
```

#### Test Issues
```bash
# Clear Vitest cache
npx vitest --run --reporter=verbose --clearCache
```

### IDE Configuration

#### VS Code Extensions
- TypeScript Importer
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- ESLint
- Prettier
- Error Lens

#### VS Code Settings (`.vscode/settings.json`)
```json
{
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.fixAll.stylelint": true
  },
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.experimental.useFlatConfig": true,
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

## Contributing

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Run quality checks: `npm run quality`
4. Update documentation if needed
5. Submit PR with clear description

### Code Review Checklist
- [ ] TypeScript types are properly defined
- [ ] Components are properly tested
- [ ] Accessibility requirements met
- [ ] Performance considerations addressed
- [ ] Documentation updated

This frontend module provides a modern, type-safe, and performant foundation for the AI-PowerPoint-Generator application, leveraging the best practices and tools in the React ecosystem.