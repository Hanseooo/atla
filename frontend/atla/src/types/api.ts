/**
 * API Type Definitions
 * 
 * Extended API types and common response structures.
 * Complements the types defined in lib/api.ts
 */

import type { Trip, TripWithDetails } from './trip'
import type { Place, SavedPlace } from './place'
import type { UserProfile, UserProfilePublic } from './user'

/**
 * Generic API response wrapper
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
 * Pagination parameters for list endpoints
 */
export interface PaginationParams {
  skip?: number
  limit?: number
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
  has_more: boolean
}

/**
 * Sort order options
 */
export type SortOrder = 'asc' | 'desc'

/**
 * Sort parameters
 */
export interface SortParams {
  sort_by?: string
  sort_order?: SortOrder
}

/**
 * Common query parameters for list endpoints
 */
export interface ListQueryParams extends PaginationParams, SortParams {
  search?: string
  filters?: Record<string, string | string[]>
}

/**
 * Success response (for delete operations, etc.)
 */
export interface SuccessResponse {
  success: boolean
  message?: string
}

// Re-export all domain types for convenience
export type { Trip, TripWithDetails, TripPublic, TripTemplate } from './trip'
export type { Place, PlacePublic, SavedPlace } from './place'
export type { UserProfile, UserProfilePublic } from './user'

// Domain-specific API response types
export type TripsResponse = ApiResponse<Trip[]>
export type TripResponse = ApiResponse<TripWithDetails>
export type PlacesResponse = ApiResponse<Place[]>
export type PlaceResponse = ApiResponse<Place>
export type SavedPlacesResponse = ApiResponse<SavedPlace[]>
export type UserProfileResponse = ApiResponse<UserProfile>
export type UserProfilePublicResponse = ApiResponse<UserProfilePublic>
