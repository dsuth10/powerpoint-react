import { PropsWithChildren, useState } from 'react'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'

export function MainLayout({ children }: PropsWithChildren) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex min-h-screen bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      {sidebarOpen && (
        <aside className="hidden w-64 shrink-0 md:block">
          <Sidebar />
        </aside>
      )}
      <div className="flex min-h-screen flex-1 flex-col">
        <Header onToggleSidebar={() => setSidebarOpen((v) => !v)} />
        <main className="container mx-auto flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  )
}

export default MainLayout


