import { createRootRoute, Outlet } from '@tanstack/react-router'
import { QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { queryClient } from '../lib/query-client'
import { useAuthStore } from '../stores/authStore'

export const Route = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  const initialize = useAuthStore((state) => state.initialize)
  const isInitialized = useAuthStore((state) => state.isInitialized)
  
  // Initialize auth on app load
  useEffect(() => {
    if (!isInitialized) {
      initialize()
    }
  }, [initialize, isInitialized])
  
  if (!isInitialized) {
    return <div>Loading...</div>
  }
  
  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  )
}
