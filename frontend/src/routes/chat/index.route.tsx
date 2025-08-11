import { Route } from '@tanstack/react-router'
import rootRoute from '../__root.route'

// Parent route for chat. Do not perform redirects here because this route
// also matches nested paths like `/chat/:sessionId` and would cause loops.
const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/chat',
})

export default route; 