import { Route } from '@tanstack/react-router'
import rootRoute from '../__root.route'

function ChatPage() {
  return (
    <div className="text-xl font-semibold">Chat Page (placeholder)</div>
  )
}

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/chat',
  component: ChatPage,
})

export default route; 