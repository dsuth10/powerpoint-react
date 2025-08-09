import { Route, useParams } from '@tanstack/react-router'
import chatRoute from './index.route'

function ChatSessionPage() {
  const { sessionId } = useParams({ from: '/chat/$sessionId' })
  return (
    <div className="text-xl font-semibold">Chat Session: {sessionId}</div>
  )
}

const route = new Route({
  getParentRoute: () => chatRoute,
  path: '$sessionId',
  component: ChatSessionPage,
})

export default route; 