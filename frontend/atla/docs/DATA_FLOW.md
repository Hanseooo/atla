# Data Flow & TanStack Query Patterns

## Overview

This document explains how data flows through our application and the patterns we use with TanStack Query for efficient server state management.

## The Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA FLOW DIAGRAM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  COMPONENT                                                   │
│     │                                                        │
│     │ 1. useTrip(tripId)                                     │
│     ▼                                                        │
│  ┌─────────────────┐                                         │
│  │   Custom Hook   │                                         │
│  │   (useTrips.ts) │                                         │
│  └────────┬────────┘                                         │
│           │ 2. useQuery({ queryKey, queryFn })              │
│           ▼                                                  │
│  ┌─────────────────┐                                         │
│  │  TanStack Query │  ← Cache Layer                         │
│  │   (QueryClient) │                                         │
│  └────────┬────────┘                                         │
│           │ 3. Cache miss → Execute queryFn                 │
│           ▼                                                  │
│  ┌─────────────────┐                                         │
│  │   Axios Client  │  ← HTTP Layer                          │
│  │    (api.ts)     │                                         │
│  └────────┬────────┘                                         │
│           │ 4. GET /api/trips/123                           │
│           ▼                                                  │
│  ┌─────────────────┐                                         │
│  │    Backend      │  ← FastAPI Server                      │
│  │   (Python)      │                                         │
│  └────────┬────────┘                                         │
│           │ 5. Return Trip + TripDays + Activities          │
│           │    (Nested JSON)                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Query Key Structure

Query keys are hierarchical and follow this pattern:

```typescript
// Level 1: Resource type
['trips']                    // All trips operations
['places']                   // All places operations
['user']                     // User profile

// Level 2: Specific identifier
['trips', userId]           // All trips for a specific user
['trips', userId, tripId]   // Specific trip
['places', 'search', query] // Place search results

// Level 3: Pagination/filters
['trips', userId, { page: 1, limit: 10 }]
['places', 'nearby', { lat: 14.5995, lng: 120.9842 }]
```

**Why this matters:**
- Easy cache invalidation: `queryClient.invalidateQueries({ queryKey: ['trips'] })`
- Granular updates: Update just one trip without affecting others
- Automatic deduplication: Same key = same request

## Hook Patterns

### 1. List Query Pattern

```typescript
// hooks/useTrips.ts
export const useTrips = (options: { page?: number; limit?: number } = {}) => {
  const { user } = useAuthStore()
  
  return useQuery({
    queryKey: ['trips', user?.id, options],
    queryFn: async () => {
      const { data } = await api.get('/api/trips', { params: options })
      return data
    },
    enabled: !!user, // Only fetch if user is logged in
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}
```

**Usage:**
```typescript
const { data: trips, isLoading, error } = useTrips({ page: 1, limit: 10 })
```

### 2. Detail Query Pattern (No Waterfalls!)

```typescript
// hooks/useTrips.ts
export const useTrip = (tripId: number) => {
  return useQuery({
    queryKey: ['trip', tripId],
    queryFn: async () => {
      // Single request returns nested data
      const { data } = await api.get(`/api/trips/${tripId}`)
      return data // { trip, trip_days: [{ activities: [...] }] }
    },
    staleTime: 1000 * 60 * 5,
    // Don't fetch if no tripId
    enabled: !!tripId,
  })
}
```

**Why nested data?**
- Avoids sequential requests (trip → days → activities)
- Single cache entry for entire trip
- Simpler component code
- Backend already supports this (see TripRepository.get_with_days)

### 3. Mutation Pattern with Optimistic Updates

```typescript
// hooks/useTrips.ts
export const useCreateTrip = () => {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  
  return useMutation({
    mutationFn: async (tripData: CreateTripInput) => {
      const { data } = await api.post('/api/trips', tripData)
      return data
    },
    
    // Optimistic update
    onMutate: async (newTrip) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['trips', user?.id] })
      
      // Snapshot previous value
      const previousTrips = queryClient.getQueryData(['trips', user?.id])
      
      // Optimistically update cache
      queryClient.setQueryData(['trips', user?.id], (old: Trip[]) => [
        { ...newTrip, id: Date.now(), isPending: true }, // Temporary ID
        ...old,
      ])
      
      // Return context for rollback
      return { previousTrips }
    },
    
    // Rollback on error
    onError: (err, newTrip, context) => {
      queryClient.setQueryData(['trips', user?.id], context?.previousTrips)
    },
    
    // Refetch after success or error
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['trips', user?.id] })
    },
  })
}
```

**Usage:**
```typescript
const createTrip = useCreateTrip()

createTrip.mutate({
  title: 'Palawan Adventure',
  destination: 'Palawan',
  days: 3,
})
```

### 4. Delete Mutation Pattern

```typescript
// hooks/useTrips.ts
export const useDeleteTrip = () => {
  const queryClient = useQueryClient()
  const { user } = useAuthStore()
  
  return useMutation({
    mutationFn: async (tripId: number) => {
      await api.delete(`/api/trips/${tripId}`)
    },
    
    onMutate: async (tripId) => {
      await queryClient.cancelQueries({ queryKey: ['trips', user?.id] })
      const previousTrips = queryClient.getQueryData(['trips', user?.id])
      
      // Remove from cache immediately
      queryClient.setQueryData(['trips', user?.id], (old: Trip[]) =>
        old.filter((trip) => trip.id !== tripId)
      )
      
      return { previousTrips }
    },
    
    onError: (err, tripId, context) => {
      queryClient.setQueryData(['trips', user?.id], context?.previousTrips)
    },
    
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['trips', user?.id] })
    },
  })
}
```

## Query Configuration Standards

### Default Options (query-client.ts)

```typescript
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data stays fresh for 5 minutes
      staleTime: 1000 * 60 * 5,
      
      // Keep unused data in cache for 10 minutes
      gcTime: 1000 * 60 * 10,
      
      // Retry failed requests once
      retry: 1,
      
      // Don't refetch when window regains focus
      refetchOnWindowFocus: false,
      
      // Refetch on reconnect
      refetchOnReconnect: true,
    },
  },
})
```

### Resource-Specific Stale Times

```typescript
// Trips - don't change often
staleTime: 1000 * 60 * 5 // 5 minutes

// Chat messages - always fresh
staleTime: 0

// Places - change occasionally
staleTime: 1000 * 60 * 1 // 1 minute

// User profile - rarely changes
staleTime: 1000 * 60 * 30 // 30 minutes
```

## Prefetching Strategy

Prefetch data before user needs it for instant navigation:

```typescript
// hooks/useTrips.ts
export const usePrefetchTrip = () => {
  const queryClient = useQueryClient()
  
  return (tripId: number) => {
    queryClient.prefetchQuery({
      queryKey: ['trip', tripId],
      queryFn: () => api.get(`/api/trips/${tripId}`),
      staleTime: 1000 * 60 * 5,
    })
  }
}

// In component
const prefetchTrip = usePrefetchTrip()

<TripCard 
  trip={trip}
  onMouseEnter={() => prefetchTrip(trip.id)} // Prefetch on hover
/>
```

## Parallel Queries

When you need multiple independent resources:

```typescript
// ❌ BAD - Sequential (slow)
const { data: trips } = useTrips()
const { data: savedPlaces } = useSavedPlaces() // Waits for trips

// ✅ GOOD - Parallel (fast)
const tripsQuery = useTrips()
const savedPlacesQuery = useSavedPlaces()
// Both fetch simultaneously

// In render
if (tripsQuery.isLoading || savedPlacesQuery.isLoading) {
  return <Loading />
}
```

## Dependent Queries

When one query depends on another:

```typescript
// Get user first, then get their trips
const { data: user } = useUser()

const { data: trips } = useTrips({
  // Only run when user exists
  enabled: !!user?.id,
})
```

## Infinite Queries (Pagination)

For paginated lists:

```typescript
// hooks/useTrips.ts
export const useInfiniteTrips = () => {
  return useInfiniteQuery({
    queryKey: ['trips', 'infinite'],
    queryFn: async ({ pageParam = 0 }) => {
      const { data } = await api.get('/api/trips', {
        params: { offset: pageParam, limit: 10 },
      })
      return data
    },
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.hasMore ? allPages.length * 10 : undefined
    },
    initialPageParam: 0,
  })
}
```

## Error Handling

### Global Error Handler

```typescript
// lib/query-client.ts
export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error) => {
      // Log to monitoring service
      console.error('Query error:', error)
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      // Show toast notification
      toast.error('Something went wrong. Please try again.')
    },
  }),
})
```

### Component-Level Error Handling

```typescript
const TripDetail = () => {
  const { data, isLoading, error } = useTrip(tripId)
  
  if (isLoading) return <TripSkeleton />
  
  if (error) {
    return (
      <ErrorBoundary 
        error={error}
        retry={() => window.location.reload()}
      />
    )
  }
  
  return <TripContent trip={data} />
}
```

## Common Patterns

### 1. Refetch After Mutation

```typescript
const mutation = useMutation({
  mutationFn: updateTrip,
  onSuccess: () => {
    // Invalidate and refetch
    queryClient.invalidateQueries({ queryKey: ['trip', tripId] })
  },
})
```

### 2. Update Cache Directly

```typescript
const mutation = useMutation({
  mutationFn: updateTrip,
  onSuccess: (data) => {
    // Update cache without refetch
    queryClient.setQueryData(['trip', tripId], data)
  },
})
```

### 3. Cancel Ongoing Requests

```typescript
const searchPlaces = useMutation({
  mutationFn: async (query: string) => {
    // Cancel previous search
    await queryClient.cancelQueries({ queryKey: ['places', 'search'] })
    
    const { data } = await api.get('/api/places/search', { params: { q: query } })
    return data
  },
})
```

## Best Practices Summary

✅ **DO:**
- Use nested data structures (no waterfalls)
- Implement optimistic updates for better UX
- Use descriptive query keys
- Set appropriate stale times
- Prefetch on hover for perceived performance
- Handle errors gracefully
- Use `enabled` option for conditional fetching

❌ **DON'T:**
- Make sequential dependent queries
- Use `any` for query data types
- Forget to invalidate cache after mutations
- Set `staleTime: 0` for static data
- Ignore loading and error states
- Mutate cache directly without proper keys

## DevTools

Enable React Query DevTools in development:

```typescript
// main.tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

Access with the floating icon in bottom-right corner during development.

## Next Steps

- Read [ROUTING.md](./ROUTING.md) for navigation patterns
- Read [STATE_MANAGEMENT.md](./STATE_MANAGEMENT.md) for client state
