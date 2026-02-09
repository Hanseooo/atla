/**
 * Trip Type Definitions
 * 
 * These types match the backend SQLModel/Pydantic models exactly.
 * Used for type-safe API communication and component props.
 */

/**
 * Activity within a trip day
 * Matches backend: app/models/trip.py - Activity
 */
export interface Activity {
  id: number
  trip_day_id: number
  name: string
  description?: string
  category: 'attraction' | 'restaurant' | 'accommodation' | 'transport'
  place_id?: string
  latitude?: number
  longitude?: number
  address?: string
  duration_minutes?: number
  cost_min?: number
  cost_max?: number
  start_time?: string  // Format: "HH:MM"
  end_time?: string
  booking_required: boolean
  booking_url?: string
  notes?: string
  sort_order: number
  created_at: string  // ISO date string
}

/**
 * Day within a trip
 * Matches backend: app/models/trip.py - TripDay
 */
export interface TripDay {
  id: number
  trip_id: number
  day_number: number
  title: string
  trip_date?: string  // ISO date string (YYYY-MM-DD)
  total_cost_min?: number
  total_cost_max?: number
  created_at: string
  activities: Activity[]
}

/**
 * Trip (itinerary)
 * Matches backend: app/models/trip.py - Trip
 */
export interface Trip {
  id: number
  user_id: string
  title: string
  summary?: string
  destination: string
  days: number
  budget?: 'low' | 'mid' | 'luxury'
  travel_style: string[]
  companions?: 'solo' | 'couple' | 'friends' | 'family'
  time_of_year?: string
  total_budget_min?: number
  total_budget_max?: number
  is_public: boolean
  view_count: number
  created_from_template_id?: number
  created_at: string
  updated_at: string
}

/**
 * Trip with nested days and activities
 * Returned by GET /api/trips/{id} with full details
 */
export interface TripWithDetails extends Trip {
  trip_days: TripDay[]
}

/**
 * Public trip view (minimal info for public listings)
 * Matches backend: TripPublic Pydantic model
 */
export interface TripPublic {
  id: number
  title: string
  summary?: string
  destination: string
  days: number
  budget?: string
  created_at: string
}

/**
 * Create trip request body
 * Matches backend: TripCreate Pydantic model
 */
export interface CreateTripRequest {
  title: string
  summary?: string
  destination: string
  days: number
  budget?: 'low' | 'mid' | 'luxury'
  travel_style?: string[]
  companions?: 'solo' | 'couple' | 'friends' | 'family'
  time_of_year?: string
  total_budget_min?: number
  total_budget_max?: number
  is_public?: boolean
}

/**
 * Update trip request body
 * Matches backend: TripUpdate Pydantic model
 */
export interface UpdateTripRequest {
  title?: string
  summary?: string
  destination?: string
  days?: number
  budget?: 'low' | 'mid' | 'luxury'
  travel_style?: string[]
  companions?: 'solo' | 'couple' | 'friends' | 'family'
  time_of_year?: string
  total_budget_min?: number
  total_budget_max?: number
  is_public?: boolean
}

/**
 * Activity detail (simplified for responses)
 * Matches backend: ActivityDetail Pydantic model
 */
export interface ActivityDetail {
  name: string
  description?: string
  category: string
  latitude?: number
  longitude?: number
  start_time?: string
  duration_minutes?: number
}

/**
 * Trip day detail (simplified for responses)
 * Matches backend: TripDayDetail Pydantic model
 */
export interface TripDayDetail {
  day_number: number
  title: string
  trip_date?: string
  activities: ActivityDetail[]
}

/**
 * Trip detail response
 * Matches backend: TripDetail Pydantic model
 */
export interface TripDetail extends TripPublic {
  trip_days: TripDayDetail[]
  total_budget_min?: number
  total_budget_max?: number
  is_public: boolean
  view_count: number
}

/**
 * Trip template for suggested itineraries
 * Matches backend: app/models/analytics.py - TripTemplate
 */
export interface TripTemplate {
  id: number
  title: string
  description?: string
  destination: string
  days: number
  budget?: string
  travel_style: string[]
  icon?: string
  template_data: Record<string, unknown>
  is_active: boolean
  sort_order: number
  created_at: string
}
