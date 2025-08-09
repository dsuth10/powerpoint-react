# AI-PowerPoint-Generator Version Matrix

## Overview
This document serves as the single source of truth for all package versions, dependencies, and configuration across the AI-PowerPoint-Generator project. All other documents must reference this file to ensure consistency.

## Frontend Dependencies

### Core Framework
| Package | Version | Rationale |
|---------|---------|-----------|
| `react` | `18.2.0` | Concurrent features, improved performance |
| `react-dom` | `18.2.0` | React DOM renderer |
| `typescript` | `~5.8.3` | Static type checking |
| `vite` | `5.1.4` | Fast build tool with HMR |
| `@vitejs/plugin-react` | `4.2.0` | React plugin for Vite |

### Routing & State Management
| Package | Version | Rationale |
|---------|---------|-----------|
| `@tanstack/router` | `1.15.0` | Type-safe routing |
| `@tanstack/react-router` | `1.15.0` | Runtime router dependency |
| `@tanstack/router-vite-plugin` | `1.127.3` | Vite plugin for file-based routing |
| `@tanstack/react-query` | `5.17.0` | Data fetching and caching |
| `zustand` | `4.5.0` | Lightweight state management |

### UI & Styling
| Package | Version | Rationale |
|---------|---------|-----------|
| `tailwindcss` | `3.4.1` | Utility-first CSS framework |
| `shadcn/ui` | `latest` | Copy-paste component library |
| `framer-motion` | `11.0.6` | Animation library |

### Forms & Validation
| Package | Version | Rationale |
|---------|---------|-----------|
| `react-hook-form` | `7.49.3` | Form management |
| `zod` | `3.22.4` | Schema validation |

### Real-time Communication
| Package | Version | Rationale |
|---------|---------|-----------|
| `socket.io-client` | `4.7.4` | WebSocket client |

### Testing & Quality
| Package | Version | Rationale |
|---------|---------|-----------|
| `vitest` | `1.2.2` | Testing framework |
| `@testing-library/react` | `14.1.2` | React testing utilities |
| `@testing-library/jest-dom` | `6.6.3` | Custom matchers for DOM assertions |
| `jsdom` | `^24.0.0` | JSDOM environment for Vitest |
| `eslint` | `^9.30.1` | Code linting |
| `prettier` | `3.2.5` | Code formatting |
| `stylelint` | `16.1.0` | CSS linting |

## Backend Dependencies

### Core Framework
| Package | Version | Rationale |
|---------|---------|-----------|
| `fastapi` | `0.111.0` | ASGI web framework |
| `uvicorn[standard]` | `0.30.1` | ASGI server |
| `pydantic` | `2.7.1` | Data validation |
| `pydantic-settings` | `2.3.0` | Settings management |

### External APIs
| Package | Version | Rationale |
|---------|---------|-----------|
| `python-pptx` | `0.6.23` | PowerPoint generation |
| `httpx` | `0.27.0` | Async HTTP client |
| `tenacity` | `8.2.3` | Retry with exponential backoff |

### Real-time Communication
| Package | Version | Rationale |
|---------|---------|-----------|
| `python-socketio` | `5.11.0` | WebSocket server (standalone) |
| `limits` | `3.12.0` | Rate limiting primitives |
| `loguru` | `0.7.2` | Structured logging |
| `prometheus-fastapi-instrumentator` | `7.0.0` | Prometheus metrics |

### Authentication & Security
| Package | Version | Rationale |
|---------|---------|-----------|
| `python-jose[cryptography]` | `3.3.0` | JWT handling |
| `passlib[bcrypt]` | `1.7.4` | Password hashing |

### Testing & Quality
| Package | Version | Rationale |
|---------|---------|-----------|
| `pytest` | `8.0.0` | Testing framework |
| `pytest-asyncio` | `0.23.0` | Async testing |
| `pytest-cov` | `4.0.0` | Coverage reporting |
| `black` | `24.0.0` | Code formatting |
| `ruff` | `0.2.0` | Fast linter |
| `mypy` | `1.8.0` | Type checking |

## Node.js & Python Versions

### Runtime Requirements
| Runtime | Version | Rationale |
|---------|---------|-----------|
| `Node.js` | `18.19.0` | LTS version with modern features |
| `Python` | `3.12.0` | Latest stable with performance improvements |

## Docker Base Images
| Image | Version |
|-------|---------|
| `node` | `18.19.0` |
| `python` | `3.12-slim` |

## CI/CD Configuration
- Node.js version: `18.19.0`
- Python version: `3.12.0`
- Ubuntu version: `ubuntu-latest`
- All versions are enforced in Docker and CI.

## Update Policy
- This document must be updated before changing any dependency version, Docker base image, or runtime version.
- All changes require approval from the technical lead before implementation.

---

**Last Updated:** 2025-07-12