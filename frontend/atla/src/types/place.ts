/**
 * Place Type Definitions
 * 
 * These types match the backend SQLModel/Pydantic models exactly.
 * Used for type-safe API communication and component props.
 */

/**
 * Place (destination, restaurant, hotel, attraction)
 * Matches backend: app/models/place.py - Place
 */
export interface Place {
  id: string  // External ID (Google Place ID, etc.)
  name: string
  description?: string
  category?: string
  latitude: number
  longitude: number
  address?: string
  phone?: string
  website?: string
  rating?: number  // 0-5
  price_level?: number  // 1-4
  opening_hours: Record<string, unknown>  // JSONB
  photos: string[]  // Array of photo URLs
  place_metadata: Record<string, unknown>  // JSONB - renamed from 'metadata' to avoid conflict
  source?: string  // 'brave_search', 'manual', etc.
  last_updated: string  // ISO date string
  created_at: string
}

/**
 * Public place view (minimal info for listings)
 * Matches backend: PlacePublic Pydantic model
 */
export interface PlacePublic {
  id: string
  name: string
  category?: string
  latitude: number
  longitude: number
  rating?: number
}

/**
 * Place detail (full info)
 * Matches backend: PlaceDetail Pydantic model
 */
export interface PlaceDetail extends PlacePublic {
  description?: string
  address?: string
  phone?: string
  website?: string
  price_level?: number
  opening_hours: Record<string, unknown>
  photos: string[]
}

/**
 * Saved place (user's bookmarked places)
 * Matches backend: app/models/place.py - SavedPlace
 */
export interface SavedPlace {
  id: number
  user_id: string
  place_id: string
  notes?: string
  created_at: string
}

/**
 * Saved place with full place details
 * Used when fetching user's saved places list
 */
export interface SavedPlaceWithDetails extends SavedPlace {
  place: Place
}

/**
 * Search places request parameters
 */
export interface SearchPlacesParams {
  query: string
  lat?: number
  lng?: number
  radius?: number  // in kilometers
  category?: string
  limit?: number
}

/**
 * Category filter options for places
 */
export type PlaceCategory = 
  | 'attraction'
  | 'restaurant'
  | 'accommodation'
  | 'transport'
  | 'shopping'
  | 'nature'
  | 'cultural'
  | 'adventure'
  | 'relaxation'
  | string  // Allow custom categories

/**
 * Place search result item
 * Simplified version for search results
 */
export interface PlaceSearchResult {
  id: string
  name: string
  category?: string
  latitude: number
  longitude: number
  address?: string
  rating?: number
  price_level?: number
  thumbnail?: string  // First photo or placeholder
}

/**
 * Opening hours structure
 * Common format for place opening hours
 */
export interface OpeningHours {
  [day: string]: {
    open: string  // "09:00"
    close: string // "18:00"
    closed?: boolean
  }
}

/**
 * Place metadata structure
 * Flexible metadata storage
 */
export interface PlaceMetadata {
  google_place_id?: string
  tripadvisor_id?: string
  tags?: string[]
  amenities?: string[]
  accessibility?: string[]
  [key: string]: unknown
}
