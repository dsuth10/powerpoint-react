import { Route, lazyRouteComponent } from '@tanstack/react-router'
import rootRoute from '../__root.route'

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/slides',
  component: lazyRouteComponent(() => import('../pages/SlidesPage')),
})

export default route; 