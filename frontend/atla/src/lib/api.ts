/**
 * API Client Configuration
 * 
 * Axios instance configured for the Philippine Travel App backend.
 * Automatically adds JWT tokens and handles authentication errors.
 */
import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/authStore'

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Standard API response wrapper
 * Matches backend Pydantic response models
 */
export interface ApiResponse<T = unknown> {
  data: T
  message?: string
}

/**
 * API Error response structure
 */
export interface ApiError {
  detail: string | { message: string; [key: string]: unknown }
  status?: number
}

/**
 * Create axios instance with default config
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // timeout: 10000, // 10 second timeout
  timeout: 60000, // 60 second timeout for testing AI operations
})

/**
 * Request interceptor
 * Adds JWT token to all requests if user is authenticated
 */
api.interceptors.request.use(
  (config) => {
    // Get token from auth store
    const session = useAuthStore.getState().session
    const token = session?.access_token

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor
 * Handles authentication errors and redirects
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Mark request as retried to prevent infinite loops
      originalRequest._retry = true

      // Check if it's a token expiration issue
      const errorDetail = error.response.data?.detail
      const isTokenExpired = 
        typeof errorDetail === 'string' && 
        (errorDetail.includes('expired') || errorDetail.includes('Token has expired'))

      if (isTokenExpired) {
        // Supabase handles token refresh automatically via auth state listener
        // Wait a moment for the refresh to complete
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // Get the new token from store
        const newSession = useAuthStore.getState().session
        const newToken = newSession?.access_token

        if (newToken) {
          // Retry the original request with new token
          originalRequest.headers = {
            ...originalRequest.headers,
            Authorization: `Bearer ${newToken}`,
          }
          return api(originalRequest)
        }
      }

      // If refresh failed or not an expiration issue, redirect to login
      const authStore = useAuthStore.getState()
      await authStore.signOut()
      
      // Redirect to login with current URL for post-login redirect
      const currentPath = window.location.pathname + window.location.search
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
      
      return Promise.reject(error)
    }

    // Handle other errors
    return Promise.reject(error)
  }
)

/**
 * Type-safe API wrapper functions
 * These provide better TypeScript support than raw axios
 */

export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.get<ApiResponse<T>>(url, config)
  return response.data.data
}

export async function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.post<ApiResponse<T>>(url, data, config)
  return response.data.data
}

export async function put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.put<ApiResponse<T>>(url, data, config)
  return response.data.data
}

export async function patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.patch<ApiResponse<T>>(url, data, config)
  return response.data.data
}

export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.delete<ApiResponse<T>>(url, config)
  return response.data.data
}

/**
 * Check if error is an authentication error
 */
export function isAuthError(error: unknown): boolean {
  return axios.isAxiosError(error) && error.response?.status === 401
}

/**
 * Extract error message from API error
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
    if (typeof detail === 'object' && detail?.message) {
      return detail.message as string
    }
    return error.message || 'An unexpected error occurred'
  }
  
  if (error instanceof Error) {
    return error.message
  }
  
  return 'An unexpected error occurred'
}

// Export the axios instance for advanced use cases
export default api
