## Working App Completion Plan

This document outlines the concrete steps to make the application fully end‑to‑end functional with the current tech stack (React 18 + TanStack Router v1, TanStack Query v5, FastAPI backend, Socket.IO WS, Zustand + immer).

### 1) Add React Query Provider

Wrap the app with a shared `QueryClientProvider` so `useMutation`/`useQuery` hooks function across the app.

```tsx
// src/providers/QueryProvider.tsx
import { PropsWithChildren, useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

export function QueryProvider({ children }: PropsWithChildren) {
  const [client] = useState(() => new QueryClient())
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
```

```tsx
// src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'
import { QueryProvider } from './providers/QueryProvider'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryProvider>
      <RouterProvider router={router} />
    </QueryProvider>
  </StrictMode>,
)
```

### 2) Align WebSocket Client with Server

- Server mounts Socket.IO at `/ws` with `socketio_path="socket.io"`.
- Client must use HTTP(S) origin with `path: '/ws/socket.io'` (not `ws://…`).
- Send `sessionId` via `auth` to join the correct room. Browsers can't set custom headers.
- Use unified events: `slide:progress`, `slide:completed`.

```ts
// src/hooks/use-websocket.ts (key init snippet)
const socket = io(window.location.origin, {
  path: '/ws/socket.io',
  transports: ['websocket'],
  auth: sessionId ? { sessionId } : undefined,
  reconnection: true,
  reconnectionAttempts: Infinity,
  reconnectionDelay: 500,
  reconnectionDelayMax: 5000,
})
// Keep listeners: 'slide:progress', 'slide:completed'
```

Remove or refactor any alternate client (e.g., `lib/slide-generation-socket.ts`) to avoid divergence.

Replace any usage of `createGenerationSocket()` with `useWebSocket()` registrations, passing the same `sessionId` used for building slides.

### 3) Backend Slide Generation Background Flow

Make `/api/v1/slides/build` actually drive progress and produce a PPTX file:

- Extend handler to accept an optional `session_id` (UUID) in the request body.
- Kick off a background task (`BackgroundTasks` or `asyncio.create_task`) that:
  - Emits incremental `slide:progress` to the `session_id` room via `emit_progress`.
  - Generates a PPTX file at `settings.PPTX_TEMP_DIR/{job_id}.pptx` (via `services/pptx.py`).
  - Emits `slide:completed` on success.
- Ensure `settings.PPTX_TEMP_DIR` exists at startup.

Sketch:

```python
# backend/app/api/slides.py
from fastapi import BackgroundTasks
from app.socketio_app import emit_progress, emit_completed
from app.services.pptx import build_pptx
import asyncio, time

@router.post('/build', ...)
async def build_slides(slides: List[dict], session_id: Optional[UUID] = None, background_tasks: BackgroundTasks = ...):
    job_id = UUID(str(uuid4()))
    def _run():
        # Emit staged progress while building
        def on_progress(done: int, total: int):
            pct = int((done / max(1, total)) * 100)
            asyncio.run(emit_progress(str(session_id or ''), { 'jobId': str(job_id), 'progress': pct }))

        # Build PPTX to temp dir; build_pptx returns a path
        path = build_pptx([SlidePlan(**s) for s in slides], output_dir=settings.PPTX_TEMP_DIR, on_progress=on_progress)
        asyncio.run(emit_completed(str(session_id or ''), { 'jobId': str(job_id), 'fileUrl': None }))
    background_tasks.add_task(_run)
    return PPTXJob(job_id=job_id, status='pending', result_url=None, error_message=None)
```

Then re‑generate the frontend OpenAPI SDK.

### 4) SlidesPage Integration (Outline → Generate → Progress → Download)

- Store the outline returned by `POST /api/v1/chat/generate` in the chat store, keyed by `sessionId`.
- In `SlidesPage`, select that outline and pass into `SlideGenerator`.
- Render `GenerationProgress` below; show `DownloadButton` when complete.

```tsx
// src/routes/pages/SlidesPage.tsx (example sketch)
import { useParams } from '@tanstack/react-router'
import { useChatStore } from '@/stores/chat-store'
import SlideGenerator from '@/components/slides/SlideGenerator'
import GenerationProgress from '@/components/slides/GenerationProgress'

export default function SlidesPage() {
  const { sessionId } = useParams({ from: '/chat/$sessionId' })
  const outline = useChatStore((s) => s.outlineBySession?.[sessionId] ?? [])
  return (
    <div className="space-y-4">
      <SlideGenerator outline={outline} sessionId={sessionId} />
      <GenerationProgress />
    </div>
  )
}
```

### 5) SDK Base URL and Optional API Key Header

Configure the generated client once and (optionally) attach `X-API-Key` for protected POST routes.

```ts
// src/lib/api/client/index.ts
import { client } from '@/lib/api/client.gen'
client.setConfig({
  baseUrl: import.meta.env.VITE_API_BASE ?? '',
  headers: { 'X-API-Key': import.meta.env.VITE_API_KEY ?? undefined },
})
export { client }
```

Ensure this module is imported at least once during app startup (e.g., in `src/main.tsx`):

```ts
// src/main.tsx
import '@/lib/api/client'
```

Env (frontend):

```env
VITE_API_BASE=http://localhost:8000
VITE_API_KEY=
```

### 6) Chat Session Handling (Minimal)

- Keep session IDs client‑side (Zustand) and validate format in the chat route `loader`.
- Optionally persist the current session ID to `localStorage` for reload continuity.

### 7) Unify WS Usage in UI

- Prefer the single `useWebSocket` hook for slide progress/completion across components.
- Remove `lib/slide-generation-socket.ts` after migration or refactor it to delegate to `useWebSocket`.

### 8) Include sessionId in Slide Builds

- Frontend `SlideGenerator` should include `sessionId` in the build request body.
- Backend `/slides/build` consumes it to route WS events to the correct room.

### 9) DownloadManager UX (Optional Polish)

- Add a small panel or header dropdown listing active/completed downloads from `downloads-store`.
- Show `Toast` notifications for completion and failures; allow clearing items.

### 10) Fix OpenAPI Generation Errors

- Start backend → ensure `/api/v1/openapi.json` is reachable.
- Run `npm run openapi:gen` in `frontend`. If errors persist, verify OpenAPI version (we force 3.0.3) and adjust hey‑api config as needed.

Troubleshooting `openapi-ts-error-*.log` with `Request failed with status 200:`:

- Generator may have fetched HTML instead of JSON (wrong URL/proxy).
- Ensure backend is running and `GET /api/v1/openapi.json` returns JSON.
- Configure the generator script to target `http://localhost:8000` (or container host) and not a file path.
- If behind Docker, ensure the script runs in a context that can reach the backend host:port.

### 11) Testing Plan

- Unit tests:
  - Query provider presence, SDK wrapper adds headers, chat/slide stores transitions, DownloadManager progress math.
  - WebSocket hook registers handlers and reconnects.
- Integration (Vitest + RTL):
  - Chat: submit prompt → optimistic user message → assistant reply.
  - Slides: build → WS progress updates → download button → DownloadManager invoked.
- Backend:
  - Background generation mock emits expected events; download endpoint serves a file.

### 12) Execution Order

1. Add QueryProvider.
2. Align Socket.IO client config; unify to `useWebSocket`.
3. Extend `/slides/build` to accept `session_id`; implement background emitter + PPTX save.
4. Regenerate OpenAPI SDK; resolve generation errors.
5. Wire `SlidesPage` to `SlideGenerator` using outline from chat store; render `GenerationProgress`.
6. Pass `sessionId` to build; ensure WS connects with the same `sessionId`.
7. Add SDK base URL + optional API key header wrapper.
8. (Optional) Persist chat session IDs client‑side.
9. (Optional) Download history panel + toasts.
10. Implement tests; run full quality suite.


