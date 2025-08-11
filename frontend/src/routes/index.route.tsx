import { Route, Navigate } from '@tanstack/react-router'
import rootRoute from './__root.route'

function getOrCreateSessionId(): string {
  const key = 'chatSessionId'
  try {
    const existing = localStorage.getItem(key)
    if (existing) return existing
    const id = Math.random().toString(36).slice(2, 10)
    localStorage.setItem(key, id)
    return id
  } catch {
    // Fallback if localStorage is unavailable
    return Math.random().toString(36).slice(2, 10)
  }
}

function IndexRedirect() {
  const sessionId = getOrCreateSessionId()
  return <Navigate to="/chat/$sessionId" params={{ sessionId }} replace />
}

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: IndexRedirect,
})

export default route;