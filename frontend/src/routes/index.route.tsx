import { Route } from '@tanstack/react-router'
import rootRoute from './__root.route'
import { useEffect, useState } from 'react'

function HomePage() {
  const [status, setStatus] = useState<'unknown' | 'ok' | 'error'>('unknown')
  const [detail, setDetail] = useState<string>('')

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/health')
        if (!cancelled) {
          setStatus(res.ok ? 'ok' : 'error')
          setDetail(`HTTP ${res.status}`)
        }
      } catch (e) {
        if (!cancelled) {
          setStatus('error')
          setDetail('Network error')
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-2">
      <div className="text-2xl font-bold">Welcome to the AI PowerPoint Generator</div>
      <div className="text-sm">Backend health: {status} {detail && `(${detail})`}</div>
    </div>
  )
}

const route = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

export default route; 