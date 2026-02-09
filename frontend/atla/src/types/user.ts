/**
 * User Type Definitions
 * 
 * These types match the backend SQLModel/Pydantic models exactly.
 * Used for type-safe API communication and component props.
 */

/**
 * User profile (extended user information)
 * Matches backend: app/models/user.py - UserProfile
 */
export interface UserProfile {
  id: string  // Matches Supabase auth.users.id
  username: string
  email: string
  display_name?: string
  avatar_url?: string
  preferences: UserPreferences
  created_at: string
  updated_at: string
}

/**
 * User preferences structure
 * Stored as JSONB in database
 */
export interface UserPreferences {
  theme?: 'light' | 'dark' | 'system'
  currency?: string  // e.g., 'PHP', 'USD'
  language?: string  // e.g., 'en', 'tl'
  notifications?: {
    email?: boolean
    push?: boolean
    trip_reminders?: boolean
    marketing?: boolean
  }
  privacy?: {
    public_profile?: boolean
    show_trips?: boolean
  }
  [key: string]: unknown  // Allow custom preferences
}

/**
 * Public user view (minimal info for public profiles)
 * Matches backend: UserProfilePublic Pydantic model
 */
export interface UserProfilePublic {
  id: string
  username: string
  display_name?: string
  avatar_url?: string
  created_at: string
}

/**
 * Create user profile request
 * Matches backend: UserProfileCreate Pydantic model
 */
export interface CreateUserProfileRequest {
  username: string
  email: string
  display_name?: string
}

/**
 * Update user profile request
 * Matches backend: UserProfileUpdate Pydantic model
 */
export interface UpdateUserProfileRequest {
  email?: string
  avatar_url?: string
  preferences?: Partial<UserPreferences>
}

/**
 * Check username availability request
 */
export interface CheckUsernameRequest {
  username: string
}

/**
 * Check username availability response
 */
export interface CheckUsernameResponse {
  available: boolean
  username: string
  message: string
}

/**
 * User session info from Supabase
 */
export interface UserSession {
  access_token: string
  refresh_token: string
  expires_at: number
  user: {
    id: string
    email: string
    user_metadata?: {
      username?: string
    }
  }
}

/**
 * Authentication error response
 */
export interface AuthError {
  message: string
  status?: number
  code?: string
}

/**
 * Login credentials
 */
export interface LoginCredentials {
  email: string
  password: string
}

/**
 * Signup credentials
 */
export interface SignupCredentials {
  email: string
  password: string
  username: string
}
