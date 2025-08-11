import { Route } from '@tanstack/react-router'
import chatRoute from './index.route'
import ChatPage from '../pages/ChatPage'
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

const route = new Route({
  getParentRoute: () => chatRoute,
  path: '$sessionId',
  // Prefetch or validate the session
  loader: async ({ params: { sessionId } }) => {
    await getSession(sessionId)
    return null
  },
  component: ChatPage,
})

export default route; 