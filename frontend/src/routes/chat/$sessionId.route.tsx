import { Route, useParams, ErrorComponentProps } from '@tanstack/react-router'
import chatRoute from './index.route'
import { useState } from 'react'
import { useRouter } from '@tanstack/react-router'

// Placeholder fetcher; swap with TanStack Query prefetch + API client
async function getSession(sessionId: string): Promise<{ id: string }> {
  // Simulate server validation/fetch
  if (!/^[a-z0-9]{3,20}$/i.test(sessionId)) {
    throw new Error('Invalid session id')
  }
  return { id: sessionId }
}

function ChatSessionPage() {
  const { sessionId } = useParams({ from: '/chat/$sessionId' })
  return (
    <div className="text-xl font-semibold">Chat Session: {sessionId}</div>
  )
}

const route = new Route({
  getParentRoute: () => chatRoute,
  path: '$sessionId',
  // Prefetch or validate the session
  loader: async ({ params: { sessionId } }) => {
    await getSession(sessionId)
    return null
  },
  errorComponent: ({ error }: ErrorComponentProps) => {
    const router = useRouter()
    const [message] = useState(error instanceof Error ? error.message : 'Failed to load session')
    return (
      <div className="space-y-2">
        <div className="text-red-600 font-medium">{message}</div>
        <button
          className="px-3 py-1 rounded bg-blue-600 text-white"
          onClick={() => router.invalidate()}
        >
          Retry
        </button>
      </div>
    )
  },
  component: ChatSessionPage,
})

export default route; 