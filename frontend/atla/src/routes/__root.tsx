import { createRootRoute, Outlet, useRouterState } from '@tanstack/react-router'
import { QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { queryClient } from '../lib/query-client'
import { useAuthStore } from '../stores/authStore'
import { BottomNav } from '../components/layout/BottomNav'
import { Header } from '../components/layout/Header'

export const Route = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  const initialize = useAuthStore((state) => state.initialize)
  const isInitialized = useAuthStore((state) => state.isInitialized)
  const user = useAuthStore((state) => state.user)

  // Access router state to hide layout elements on auth pages
  const routerState = useRouterState()
  const isAuthPage = ['/login', '/signup'].includes(routerState.location.pathname)

  // Initialize auth on app load
  useEffect(() => {
    if (!isInitialized) {
      initialize()
    }
  }, [initialize, isInitialized])

  if (!isInitialized) {
    return <div>Loading...</div>
  }

  const showLayout = user && !isAuthPage

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex min-h-screen flex-col">
        {showLayout && <Header />}
        <main className="flex-1">
          <Outlet />
        </main>
        {showLayout && <BottomNav />}
      </div>
    </QueryClientProvider>
  )
}
