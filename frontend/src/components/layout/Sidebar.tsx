import { Link, useRouterState } from '@tanstack/react-router'
import { useState } from 'react'

export function Sidebar() {
  const [open, setOpen] = useState(true)
  const activePath = useRouterState({ select: (s) => s.location.pathname })

  const linkClass = (to: string) =>
    `block rounded px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 ${
      activePath.startsWith(to)
        ? 'bg-gray-100 font-medium dark:bg-gray-800'
        : 'text-gray-700 dark:text-gray-300'
    }`

  return (
    <nav aria-label="Sidebar" className="h-full w-64 border-r bg-gray-50 p-3 dark:border-gray-800 dark:bg-gray-950">
      <button
        className="mb-3 inline-flex rounded border px-2 py-1 text-xs text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="sidebar-links"
      >
        {open ? 'Collapse' : 'Expand'}
      </button>
      <div id="sidebar-links" role="navigation" className={open ? 'space-y-1' : 'hidden'}>
        <Link to="/chat" className={linkClass('/chat')}>
          Chat
        </Link>
        <Link to="/slides" className={linkClass('/slides')}>
          Slides
        </Link>
      </div>
    </nav>
  )
}

export default Sidebar


