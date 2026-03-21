import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabase, type User, type Session } from '../lib/supabase'
import api from '../lib/api'
import { router } from '../router'
import { queryClient } from '../lib/query-client'
import type { UserProfile, CheckUsernameResponse } from '../types'

interface ProfileCreationError {
  message: string
  canRetry: boolean
}

interface AuthState {
  // State
  user: User | null
  session: Session | null
  profile: UserProfile | null
  isLoading: boolean
  isInitialized: boolean
  profileCreationError: ProfileCreationError | null
  
  // Actions
  initialize: () => Promise<void>
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, username: string) => Promise<void>
  signOut: () => Promise<void>
  checkUsername: (username: string) => Promise<CheckUsernameResponse>
  createUserProfile: (username: string, email: string) => Promise<void>
  updateProfile: (data: { email?: string; avatar_url?: string; preferences?: Record<string, unknown> }) => Promise<void>
  retryProfileCreation: () => Promise<void>
  clearProfileError: () => void
  setUser: (user: User | null) => void
  setSession: (session: Session | null) => void
  setProfile: (profile: UserProfile | null) => void
  setIsLoading: (isLoading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      session: null,
      profile: null,
      isLoading: false,
      isInitialized: false,
      profileCreationError: null,
      
      // Initialize auth state from Supabase session
      initialize: async () => {
        try {
          const { data: { session } } = await supabase.auth.getSession()
          
          // Set session in state first so api.ts interceptor can use the token!
          set({ session, user: session?.user ?? null })

          // If session exists, fetch user profile
          let profile: UserProfile | null = null
          if (session?.user) {
            try {
              const response = await api.get<UserProfile>('/auth/me')
              profile = response.data
            } catch {
              // Profile doesn't exist yet (edge case from email confirmation)
              console.warn('Profile not found for user, attempting to create one automatically...')
              
              // Safety Net: Auto-create profile if missing
              if (session.user.email) {
                try {
                  const fallbackUsername = session.user.email.split('@')[0].replace(/[^a-zA-Z0-9_]/g, '') + Math.floor(Math.random() * 1000);
                  const username = session.user.user_metadata?.username || fallbackUsername;
                  
                  const response = await api.post<UserProfile>('/auth/profile', {
                    username: username.toLowerCase(),
                    email: session.user.email,
                  })
                  profile = response.data
                  console.log('Profile auto-created successfully during initialization!');
                } catch (createError) {
                  console.error('Auto-creation failed during init:', createError);
                }
              }
            }
          }
          
          set({ 
            profile,
            isInitialized: true 
          })
        } catch (error) {
          console.error('Auth initialization error:', error)
          set({ isInitialized: true })
        }
      },
      
      // Sign in with email/password
      signIn: async (email, password) => {
        set({ isLoading: true, profileCreationError: null })
        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
          })
          
          if (error) throw error

          // Persist Supabase session before backend calls so Authorization
          // header is available for immediate authenticated requests.
          set({
            user: data.user,
            session: data.session,
          })
          
          // Fetch user profile after login
          let profile: UserProfile | null = null
          try {
            const response = await api.get<UserProfile>('/auth/me')
            profile = response.data
          } catch {
            // Profile doesn't exist (likely due to email confirmation delay)
            console.warn('Profile not found, attempting to create one automatically...')
            
            // Safety Net: Auto-create profile if missing
            if (data.user?.email) {
              try {
                // Generate a fallback username if metadata is missing
                const fallbackUsername = data.user.email.split('@')[0].replace(/[^a-zA-Z0-9_]/g, '') + Math.floor(Math.random() * 1000);
                const username = data.user.user_metadata?.username || fallbackUsername;
                
                const response = await api.post<UserProfile>('/auth/profile', {
                  username: username.toLowerCase(),
                  email: data.user.email,
                })
                profile = response.data
                console.log('Profile auto-created successfully!');
              } catch (createError) {
                console.error('Auto-creation failed:', createError);
              }
            }
          }
          
          set({ 
            profile,
            isLoading: false 
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      // Sign up with email/password + backend profile creation
      signUp: async (email, password, username) => {
        set({ isLoading: true, profileCreationError: null })
        try {
          // Step 1: Supabase signup
          const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
              data: { username },
            },
          })
          
          if (error) throw error

          // Persist Supabase session before backend profile setup call.
          set({
            user: data.user,
            session: data.session,
          })
          
          // Step 2: Create/enrich profile via backend API
          // This updates the trigger-created profile with username
          try {
            const response = await api.post<UserProfile>('/auth/profile', {
              username,
              email,
            })
            
            set({ 
              profile: response.data,
              isLoading: false 
            })
          } catch (profileError: unknown) {
            const err = profileError as { response?: { data?: { detail?: string } } };
            // Profile creation failed - handle gracefully (Option B)
            console.error('Profile creation failed:', err)
            
            // Store error for UI to display retry option
            set({
              user: data.user,
              session: data.session,
              isLoading: false,
              profileCreationError: {
                message: err.response?.data?.detail || 'Failed to complete profile setup. Please try again.',
                canRetry: true
              }
            })
            
            // Don't throw - user is still authenticated with Supabase
            // They can retry profile creation
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      // Check username availability
      checkUsername: async (username: string): Promise<CheckUsernameResponse> => {
        const response = await api.get<CheckUsernameResponse>(`/auth/check-username?username=${encodeURIComponent(username)}`)
        return response.data
      },
      
      // Create user profile (called separately or for retry)
      createUserProfile: async (username: string, email: string) => {
        set({ isLoading: true, profileCreationError: null })
        try {
          const response = await api.post<UserProfile>('/auth/profile', {
            username,
            email,
          })
          
          set({
            profile: response.data,
            isLoading: false,
            profileCreationError: null
          })
        } catch (error: unknown) {
          const err = error as { response?: { data?: { detail?: string } } };
          set({
            isLoading: false,
            profileCreationError: {
              message: err.response?.data?.detail || 'Failed to create profile. Please try again.',
              canRetry: true
            }
          })
          throw error
        }
      },
      
      // Update user profile
      updateProfile: async (data) => {
        set({ isLoading: true });
        try {
          const response = await api.patch<UserProfile>('/auth/profile', data);
          set({ profile: response.data, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      // Retry profile creation with stored credentials
      retryProfileCreation: async () => {
        const state = get()
        const user = state.user
        
        if (!user?.email) {
          throw new Error('No user email found')
        }
        
        // Get username from Supabase user metadata
        const username = user.user_metadata?.username
        if (!username) {
          throw new Error('No username found')
        }
        
        await get().createUserProfile(username, user.email)
      },
      
      // Clear profile creation error
      clearProfileError: () => {
        set({ profileCreationError: null })
      },
      
      // Sign out
      signOut: async () => {
        await supabase.auth.signOut()
        set({ user: null, session: null, profile: null, profileCreationError: null })
        // Clear all React Query caches (Trips, Places, etc.) to prevent data bleed between accounts
        queryClient.clear()
        // Navigate to login page after logout
        router.navigate({ to: '/login' })
      },
      
      setUser: (user) => set({ user }),
      setSession: (session) => set({ session }),
      setProfile: (profile) => set({ profile }),
      setIsLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        session: state.session 
      }),
    }
  )
)
