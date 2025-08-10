import { RootRoute, Outlet } from '@tanstack/react-router'
import { Suspense } from 'react'
import MainLayout from '@/components/layout/MainLayout'
import LoadingState from '@/components/ui/LoadingState'

function RootLayout() {
  return (
    <MainLayout>
      <Suspense fallback={<LoadingState />}> 
        <Outlet />
      </Suspense>
    </MainLayout>
  )
}

const rootRoute = new RootRoute({
  component: RootLayout,
})

export default rootRoute; 