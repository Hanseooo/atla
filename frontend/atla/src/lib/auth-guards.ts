import { redirect } from '@tanstack/react-router'
import { supabase } from './supabase'

/**
 * Require authentication - redirects to login if not authenticated
 * Preserves the current URL so user can be redirected back after login
 */
export async function requireAuth({ location }: { location: { href: string } }) {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    throw redirect({
      to: '/login',
      search: { redirect: location.href },
    })
  }
}

/**
 * Require guest - redirects to home if already authenticated
 * Use this for login/signup pages
 */
export async function requireGuest() {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (session) {
    throw redirect({ to: '/home' })
  }
}

/**
 * Redirect authenticated - redirects to home if user is already logged in
 * Use this for the landing page to skip it for active users
 */
export async function redirectAuthenticated() {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (session) {
    throw redirect({ to: '/home' })
  }
}

/**
 * Optional auth - doesn't redirect, just returns auth status
 * Use this when you want to show different content based on auth status
 */
export async function optionalAuth() {
  const { data: { session } } = await supabase.auth.getSession()
  return { isAuthenticated: !!session, session }
}
