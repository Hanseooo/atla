import api, { post, put, del } from './api';
import type { 
  Trip, 
  TripWithDetails, 
  CreateTripRequest, 
  UpdateTripRequest 
} from '../types/trip';

/**
 * Trip API Client
 * 
 * Handles all communication with the backend Trips API endpoints.
 */
export const tripApi = {
  /**
   * Fetch a list of trips for the current authenticated user
   */
  async getTrips(skip = 0, limit = 20): Promise<Trip[]> {
    // The backend returns a raw list [] for this endpoint, not wrapped in { data: [] }
    const response = await api.get<Trip[]>(`/api/trips/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  /**
   * Fetch a specific trip by its ID, including all days and activities
   */
  async getTrip(tripId: number): Promise<TripWithDetails> {
    // The backend returns a raw object {} for this endpoint, not wrapped in { data: {} }
    const response = await api.get<TripWithDetails>(`/api/trips/${tripId}`);
    return response.data;
  },

  /**
   * FUTURE USE: Create a new trip
   * Backend endpoint exists, but UI relies on chat.
   */
  async createTrip(data: CreateTripRequest): Promise<Trip> {
    return await post<Trip>('/api/trips/', data);
  },

  /**
   * FUTURE USE: Update an existing trip
   * NOTE: Backend endpoint PATCH /api/trips/{id} does not exist yet.
   */
  async updateTrip(tripId: number, data: UpdateTripRequest): Promise<Trip> {
    return await put<Trip>(`/api/trips/${tripId}`, data);
  },

  /**
   * FUTURE USE: Delete a trip
   * NOTE: Backend endpoint DELETE /api/trips/{id} does not exist yet.
   */
  async deleteTrip(tripId: number): Promise<void> {
    return await del<void>(`/api/trips/${tripId}`);
  }
};
