import { Route, useParams } from '@tanstack/react-router'
import slidesRoute from './index.route'

function SlidePage() {
  const { slideId } = useParams({ from: '/slides/$slideId' })
  return (
    <div className="text-xl font-semibold">Slide: {slideId}</div>
  )
}

const route = new Route({
  getParentRoute: () => slidesRoute,
  path: '$slideId',
  component: SlidePage,
})

export default route; 