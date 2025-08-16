import { Route, lazyRouteComponent } from '@tanstack/react-router'
import rootRoute from '../__root.route'

// Route for /slides (no sessionId)
const slidesRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/slides',
  component: lazyRouteComponent(() => import('../pages/SlidesPage')),
})

// Route for /slides/$sessionId  
const slidesSessionRoute = new Route({
  getParentRoute: () => slidesRoute,
  path: '$sessionId',
  component: lazyRouteComponent(() => import('../pages/SlidesPage')),
})

export { slidesSessionRoute }
export default slidesRoute; 