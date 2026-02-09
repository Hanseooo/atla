import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuthStore } from '../stores/authStore'

/**
 * Hook for checking username availability with debouncing and race condition protection
 * 
 * Usage:
 * const { isAvailable, isChecking, error, checkUsername } = useUsernameCheck()
 * 
 * // Call checkUsername whenever input changes
 * useEffect(() => {
 *   checkUsername(username)
 * }, [username])
 */
export function useUsernameCheck(debounceMs: number = 500) {
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null)
  const [isChecking, setIsChecking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Use ref instead of state to avoid re-renders
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  // Track request ID to prevent race conditions
  const requestIdRef = useRef<number>(0)
  
  const checkUsername = useCallback(async (username: string) => {
    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    
    // Reset state
    setIsAvailable(null)
    setError(null)
    
    // Validate format
    if (!username || username.length < 3) {
      return
    }
    
    // Validate username format (letters, numbers, underscores only)
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      setError('Username can only contain letters, numbers, and underscores')
      setIsAvailable(false)
      return
    }
    
    // Increment request ID for this check
    const currentRequestId = ++requestIdRef.current
    
    // Debounce check
    timeoutRef.current = setTimeout(async () => {
      // Only update loading state if this is still the latest request
      if (currentRequestId === requestIdRef.current) {
        setIsChecking(true)
      }
      
      try {
        const check = await useAuthStore.getState().checkUsername(username)
        
        // Only update state if this is still the latest request
        // This prevents race conditions where an older request completes after a newer one
        if (currentRequestId === requestIdRef.current) {
          setIsAvailable(check.available)
          if (!check.available) {
            setError(check.message || 'Username is already taken')
          }
        }
      } catch (err: any) {
        // Only update error if this is still the latest request
        if (currentRequestId === requestIdRef.current) {
          setError('Failed to check username availability')
        }
      } finally {
        // Only update loading state if this is still the latest request
        if (currentRequestId === requestIdRef.current) {
          setIsChecking(false)
        }
      }
    }, debounceMs)
  }, [debounceMs])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])
  
  return {
    isAvailable,
    isChecking,
    error,
    checkUsername
  }
}
