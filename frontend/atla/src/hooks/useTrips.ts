import { useQuery, useMutation, useQueryClient, type UseQueryResult, type UseMutationResult } from '@tanstack/react-query';
import { tripApi } from '../lib/trip-api';
import type { CreateTripRequest, UpdateTripRequest, Trip, TripWithDetails } from '../types/trip';

/**
 * TRIP HOOKS
 * 
 * NOTES:
 * - Queries (useUserTrips, useTripDetail): Wired up to live backend GET endpoints.
 * - Mutations (useCreateTrip, useUpdateTrip, useDeleteTrip): Proactively built and typed 
 *   to match the trip.ts interfaces. The backend DELETE/PATCH endpoints do not exist yet, 
 *   but these are ready for immediate use once future issue adds them.
 * - Caching: Strictly adheres to ARCHITECTURE.md (5-minute stale time for trips).
 */

// Query Key Factory pattern for consistent cache invalidation
export const tripKeys = {
  all: ['trips'] as const,
  lists: () => [...tripKeys.all, 'list'] as const,
  list: (filters: string) => [...tripKeys.lists(), { filters }] as const,
  details: () => [...tripKeys.all, 'detail'] as const,
  detail: (id: number) => [...tripKeys.details(), id] as const,
};

/**
 * Fetches a paginated list of trips for the current authenticated user.
 * Currently used on the HomePage and TripsPage.
 */
export function useUserTrips(skip = 0, limit = 20): UseQueryResult<Trip[], Error> {
  return useQuery({
    queryKey: tripKeys.list(`skip=${skip}-limit=${limit}`),
    queryFn: () => tripApi.getTrips(skip, limit),
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes as per ARCHITECTURE.md
  });
}

/**
 * Fetches the deep details of a specific trip (including all days and activities).
 * Currently used when navigating to the TripDetailPage.
 */
export function useTripDetail(tripId: number): UseQueryResult<TripWithDetails, Error> {
  return useQuery({
    queryKey: tripKeys.detail(tripId),
    queryFn: () => tripApi.getTrip(tripId),
    enabled: !!tripId,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}

/**
 * FUTURE USE: Creates a new trip manually.
 * The backend POST endpoint exists, but the UI currently relies on AI chat to create trips.
 * This is pre-built for future manual trip creation features.
 */
export function useCreateTrip(): UseMutationResult<Trip, Error, CreateTripRequest, unknown> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTripRequest) => tripApi.createTrip(data),
    onSuccess: () => {
      // Invalidate and refetch the list of trips when a new one is created
      queryClient.invalidateQueries({ queryKey: tripKeys.lists() });
    },
  });
}

/**
 * FUTURE USE: Updates an existing trip's details.
 * NOTE: The backend PATCH /api/trips/{id} endpoint does NOT exist yet!
 * This hook is pre-built and ready to use once the backend supports it.
 */
export function useUpdateTrip(): UseMutationResult<Trip, Error, { id: number; data: UpdateTripRequest }, unknown> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTripRequest }) => 
      tripApi.updateTrip(id, data),
    onSuccess: (data) => {
      // Invalidate specific trip and the general list
      queryClient.invalidateQueries({ queryKey: tripKeys.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: tripKeys.lists() });
    },
  });
}

/**
 * FUTURE USE: Deletes a specific trip.
 * NOTE: The backend DELETE /api/trips/{id} endpoint does NOT exist yet!
 * This hook is pre-built and ready to use once the backend supports it.
 */
export function useDeleteTrip(): UseMutationResult<void, Error, number, unknown> {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tripId: number) => tripApi.deleteTrip(tripId),
    onSuccess: (_, variables) => {
      queryClient.removeQueries({ queryKey: tripKeys.detail(variables) });
      queryClient.invalidateQueries({ queryKey: tripKeys.lists() });
    },
  });
}
