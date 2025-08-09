import { Route } from '@tanstack/react-router'
import rootRoute from '../__root.route'

function SlidesPage() {
  return (
    <div className="text-xl font-semibold">Slides Page (placeholder)</div>
  )
}

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/slides',
  component: SlidesPage,
})

export default route; 