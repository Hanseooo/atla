import { useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { supabase } from '../lib/supabase'

export function useAuth() {
  const { user, session, isLoading, isInitialized, initialize, setUser, setSession } = useAuthStore()
  
  // Initialize auth on mount
  useEffect(() => {
    if (!isInitialized) {
      initialize()
    }
  }, [isInitialized, initialize])
  
  // Listen for auth state changes
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user ?? null)
        setSession(session)
        
        // Handle specific events
        if (event === 'SIGNED_IN') {
          console.log('User signed in')
        } else if (event === 'SIGNED_OUT') {
          console.log('User signed out')
        }
      }
    )
    
    return () => {
      subscription.unsubscribe()
    }
  }, [setUser, setSession])
  
  return {
    user,
    session,
    isLoading,
    isInitialized,
    isAuthenticated: !!user,
  }
}
