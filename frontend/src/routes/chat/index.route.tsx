import { Route, lazyRouteComponent } from '@tanstack/react-router'
import rootRoute from '../__root.route'

// Route for /chat (no sessionId) - will show ChatPage directly
const chatRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/chat',
  component: lazyRouteComponent(() => import('../pages/ChatPage')),
})

// Route for /chat/$sessionId  
const chatSessionRoute = new Route({
  getParentRoute: () => chatRoute,
  path: '$sessionId',
  component: lazyRouteComponent(() => import('../pages/ChatPage')),
})

export { chatSessionRoute }
export default chatRoute 