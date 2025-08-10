import { Route, redirect } from '@tanstack/react-router'
import rootRoute from './__root.route'

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: '/chat', replace: true })
  },
})

export default route;