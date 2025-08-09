import { RootRoute, Outlet } from '@tanstack/react-router'

function RootLayout() {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-100 dark:bg-gray-900 p-4">
        {/* Sidebar placeholder */}
        <div className="font-bold">Sidebar</div>
      </aside>
      <main className="flex-1 p-6">
        {/* The outlet will be rendered here by TanStack Router */}
        <Outlet />
      </main>
    </div>
  )
}

const rootRoute = new RootRoute({
  component: RootLayout,
})

export default rootRoute; 