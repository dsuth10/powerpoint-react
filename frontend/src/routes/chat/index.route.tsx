import { Route, lazyRouteComponent, redirect } from '@tanstack/react-router'
import rootRoute from '../__root.route'
// Placeholder async creator; replace with API hook call when available
async function createOrResolveChatSessionId(): Promise<string> {
  // TODO: integrate with real API client in hooks/api
  // For now, generate a simple random id stub
  const id = Math.random().toString(36).slice(2, 10)
  return Promise.resolve(id)
}

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/chat',
  // If no session id provided, create or resolve and redirect
  beforeLoad: async () => {
    const sessionId = await createOrResolveChatSessionId()
    throw redirect({ to: '/chat/$sessionId', params: { sessionId }, replace: true })
  },
  component: lazyRouteComponent(() => import('../pages/ChatPage')),
})

export default route; 