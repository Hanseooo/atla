/**
 * Type Definitions Barrel Export
 * 
 * Import all types from this file:
 * import { Trip, Place, UserProfile, ApiResponse } from '@/types'
 */

// Trip types
export type {
  Activity,
  TripDay,
  Trip,
  TripWithDetails,
  TripPublic,
  CreateTripRequest,
  UpdateTripRequest,
  ActivityDetail,
  TripDayDetail,
  TripDetail,
  TripTemplate,
} from './trip'

// Place types
export type {
  Place,
  PlacePublic,
  PlaceDetail,
  SavedPlace,
  SavedPlaceWithDetails,
  SearchPlacesParams,
  PlaceCategory,
  PlaceSearchResult,
  OpeningHours,
  PlaceMetadata,
} from './place'

// User types
export type {
  UserProfile,
  UserPreferences,
  UserProfilePublic,
  CreateUserProfileRequest,
  UpdateUserProfileRequest,
  CheckUsernameRequest,
  CheckUsernameResponse,
  UserSession,
  AuthError,
  LoginCredentials,
  SignupCredentials,
} from './user'

// API types
export type {
  ApiResponse,
  ApiError,
  PaginationParams,
  PaginatedResponse,
  SortOrder,
  SortParams,
  ListQueryParams,
  SuccessResponse,
  // Re-export domain types
  Trip as ApiTrip,
  TripWithDetails as ApiTripWithDetails,
  TripPublic as ApiTripPublic,
  TripTemplate as ApiTripTemplate,
  Place as ApiPlace,
  PlacePublic as ApiPlacePublic,
  SavedPlace as ApiSavedPlace,
  UserProfile as ApiUserProfile,
  UserProfilePublic as ApiUserProfilePublic,
  // Response types
  TripsResponse,
  TripResponse,
  PlacesResponse,
  PlaceResponse,
  SavedPlacesResponse,
  UserProfileResponse,
  UserProfilePublicResponse,
} from './api'
