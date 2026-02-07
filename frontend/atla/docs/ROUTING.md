# Routing Guide

## Overview

We use **TanStack Router** with file-based routing. This means the file structure in `src/routes/` directly determines your URL structure.

## Why File-Based Routing?

```
Traditional (React Router)          File-Based (TanStack Router)
─────────────────────────          ─────────────────────────────
const routes = [                   src/routes/
  { path: '/',                     ├── index.tsx     → /
    component: Home },             ├── trips/
  { path: '/trips',                │   ├── index.tsx → /trips
    component: Trips },            │   └── $tripId.tsx → /trips/123
  { path: '/trips/:id',            └── profile/
    component: TripDetail },          └── index.tsx → /profile
]
```

**Benefits:**
- ✅ Automatic type safety
- ✅ Code splitting by route
- ✅ No manual route configuration
- ✅ Nested layouts supported
- ✅ Type-safe navigation

## Route File Conventions

### Basic Routes

| File | URL | Description | Auth Required |
|------|-----|-------------|---------------|
| `index.tsx` | `/` | Home page (Trip Dashboard) | ✅ Yes |
| `chat.tsx` | `/chat` | AI trip planning chat | ✅ Yes |
| `trips.index.tsx` | `/trips` | Trips list page | ✅ Yes |
| `trips.$tripId.tsx` | `/trips/123` | Trip detail (dynamic param) | ✅ Yes |
| `explore.index.tsx` | `/explore` | Explore places | ✅ Yes |
| `profile.index.tsx` | `/profile` | User profile | ✅ Yes |
| `login.tsx` | `/login` | Login page | ❌ Guest only |
| `signup.tsx` | `/signup` | Signup page | ❌ Guest only |

### File Naming Rules

```
Pattern              →  Meaning
─────────────────────────────────────────
index.tsx            →  Default route for the folder
$param.tsx           →  Dynamic route parameter
file.index.tsx       →  Nested route with layout prefix
(underscore).tsx     →  Route without layout wrapper
layout.tsx           →  Layout file for nested routes
```

### Special Characters

- `$` - Dynamic parameter: `trips.$tripId.tsx` → `/trips/:tripId`
- `_` - No layout: `_auth.login.tsx` → `/login` (without root layout)
- `.` - Nested: `trips.index.tsx` → `/trips`

## Route Structure

```
routes/
├── __root.tsx                    # Root layout (applies to all routes)
│   ├── index.tsx                 # / (Home - Trip Dashboard)
│   ├── chat.tsx                  # /chat (AI trip planning)
│   ├── trips/
│   │   ├── index.tsx             # /trips (Trips list)
│   │   └── $tripId.tsx           # /trips/123 (Trip detail)
│   ├── explore/
│   │   └── index.tsx             # /explore (Browse places)
│   ├── profile/
│   │   └── index.tsx             # /profile (User settings)
│   ├── login.tsx                 # /login (Auth page)
│   └── signup.tsx                # /signup (Auth page)
```

## Creating Routes

### 1. Simple Route

```typescript
// routes/index.tsx (Chat page)
import { createFileRoute } from '@tanstack/react-router'
import { ChatInterface } from '../components/chat/ChatInterface'

export const Route = createFileRoute('/')({
  component: ChatPage,
})

function ChatPage() {
  return (
    <div className="h-full">
      <ChatInterface />
    </div>
  )
}
```

### 2. Route with Parameters

```typescript
// routes/trips.$tripId.tsx
import { createFileRoute, useParams } from '@tanstack/react-router'
import { useTrip } from '../hooks/useTrips'
import { TripDetail } from '../components/trips/TripDetail'

export const Route = createFileRoute('/trips/$tripId')({
  component: TripDetailPage,
  // Parse params (optional)
  parseParams: (params) => ({
    tripId: Number(params.tripId),
  }),
  // Validate params (optional)
  validateSearch: (search) => ({
    tab: (search.tab as 'itinerary' | 'map' | 'budget') || 'itinerary',
  }),
})

function TripDetailPage() {
  const { tripId } = useParams({ from: '/trips/$tripId' })
  const { data: trip, isLoading } = useTrip(tripId)
  
  if (isLoading) return <TripSkeleton />
  
  return <TripDetail trip={trip} />
}
```

### 3. Route with Search Params

```typescript
// URL: /trips/123?tab=map&edit=true

function TripDetailPage() {
  const { tripId } = useParams({ from: '/trips/$tripId' })
  const { tab, edit } = useSearch({ from: '/trips/$tripId' })
  
  // tab = 'map'
  // edit = true
  
  return (
    <Tabs value={tab}>
      <TabsList>
        <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
        <TabsTrigger value="map">Map</TabsTrigger>
        <TabsTrigger value="budget">Budget</TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
```

### 4. Protected Route

```typescript
// routes/trips.index.tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { supabase } from '../lib/supabase'

export const Route = createFileRoute('/trips')({
  component: TripsPage,
  beforeLoad: async ({ location }) => {
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      throw redirect({
        to: '/login',
        search: {
          // Redirect back to this page after login
          redirect: location.href,
        },
      })
    }
  },
})

function TripsPage() {
  return <TripsList />
}
```

### 5. Route with Loader (Data Prefetching)

```typescript
// routes/trips.$tripId.tsx
import { createFileRoute } from '@tanstack/react-router'
import { queryClient } from '../lib/query-client'
import { fetchTrip } from '../api/trips'

export const Route = createFileRoute('/trips/$tripId')({
  component: TripDetailPage,
  loader: async ({ params }) => {
    // Prefetch trip data before rendering
    await queryClient.prefetchQuery({
      queryKey: ['trip', params.tripId],
      queryFn: () => fetchTrip(params.tripId),
    })
    
    return { tripId: params.tripId }
  },
})
```

## Root Layout

The `__root.tsx` file wraps ALL routes:

```typescript
// routes/__root.tsx
import { createRootRoute, Outlet } from '@tanstack/react-router'
import { QueryClientProvider } from '@tanstack/react-query'
import { AnimatePresence } from 'framer-motion'
import { queryClient } from '../lib/query-client'
import { BottomNav } from '../components/layout/BottomNav'

export const Route = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        {/* Page content */}
        <main className="pb-20"> {/* Space for bottom nav */}
          <AnimatePresence mode="wait">
            <Outlet /> {/* Current route renders here */}
          </AnimatePresence>
        </main>
        
        {/* Bottom navigation (hidden on auth pages) */}
        <BottomNav />
      </div>
    </QueryClientProvider>
  )
}
```

## Navigation

### Programmatic Navigation

```typescript
import { useNavigate, useRouter } from '@tanstack/react-router'

function TripCard({ trip }: { trip: Trip }) {
  const navigate = useNavigate()
  const router = useRouter()
  
  const handleClick = () => {
    // Navigate to trip detail
    navigate({
      to: '/trips/$tripId',
      params: { tripId: trip.id },
      search: { tab: 'itinerary' },
    })
    
    // Or use router
    router.navigate({
      to: '/trips/$tripId',
      params: { tripId: trip.id },
    })
  }
  
  return <Card onClick={handleClick}>{trip.title}</Card>
}
```

### Link Component

```typescript
import { Link } from '@tanstack/react-router'

function Navigation() {
  return (
    <nav>
      <Link 
        to="/trips/$tripId" 
        params={{ tripId: 123 }}
        search={{ tab: 'map' }}
        activeProps={{ className: 'text-primary' }}
      >
        View Trip
      </Link>
    </nav>
  )
}
```

### Type-Safe Navigation

TanStack Router generates types from your routes:

```typescript
// Fully typed! Autocomplete works
navigate({ 
  to: '/trips/$tripId',  // ✅ Autocomplete shows available routes
  params: { 
    tripId: 123,          // ✅ Type-checked: must be number
  },
  search: {
    tab: 'itinerary',     // ✅ Type-checked: must be valid tab
  },
})
```

## Route Guards (Centralized)

We use centralized auth guard functions in `src/lib/auth-guards.ts` for consistent authentication across routes.

### Available Guards

```typescript
// src/lib/auth-guards.ts

/**
 * Require authentication - redirects to login if not authenticated
 * Preserves the current URL so user can be redirected back after login
 */
export async function requireAuth({ location }: { location: { href: string } }) {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    throw redirect({
      to: '/login',
      search: { redirect: location.href },
    })
  }
}

/**
 * Require guest - redirects to home if already authenticated
 * Use this for login/signup pages
 */
export async function requireGuest() {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (session) {
    throw redirect({ to: '/' })
  }
}

/**
 * Optional auth - doesn't redirect, just returns auth status
 * Use this when you want to show different content based on auth status
 */
export async function optionalAuth() {
  const { data: { session } } = await supabase.auth.getSession()
  return { isAuthenticated: !!session, session }
}
```

### Protected Routes (requireAuth)

```typescript
// routes/trips.index.tsx
import { createFileRoute } from '@tanstack/react-router'
import { requireAuth } from '../lib/auth-guards'

export const Route = createFileRoute('/trips')({
  component: TripsPage,
  beforeLoad: requireAuth,
})

function TripsPage() {
  return <TripsList />
}
```

**Protected routes in our app:**
- `/` (Home - Trip Dashboard)
- `/trips`
- `/trips/:tripId`
- `/explore`
- `/profile`
- `/chat`

### Guest-Only Routes (requireGuest)

```typescript
// routes/login.tsx
import { createFileRoute } from '@tanstack/react-router'
import { requireGuest } from '../lib/auth-guards'

export const Route = createFileRoute('/login')({
  component: LoginPage,
  beforeLoad: requireGuest,
})

function LoginPage() {
  // This page is only accessible to non-authenticated users
  return <LoginForm />
}
```

**Guest-only routes in our app:**
- `/login`
- `/signup`

### How It Works

1. **User visits protected route without auth:**
   - Guard detects no session
   - Redirects to `/login?redirect=/original-path`
   - User logs in
   - Redirected back to original page

2. **User visits guest-only route while authenticated:**
   - Guard detects active session
   - Redirects to `/` (home)
   - Prevents logged-in users from seeing login pages

3. **Adding a new protected route:**
   ```typescript
   import { requireAuth } from '../lib/auth-guards'
   
   export const Route = createFileRoute('/new-page')({
     component: NewPage,
     beforeLoad: requireAuth, // One line for full protection
   })
   ```

### Benefits of Centralized Guards

✅ **Single source of truth** - Auth logic in one place  
✅ **Consistent behavior** - All routes behave the same way  
✅ **Easy to modify** - Change auth logic once, affects all routes  
✅ **DRY principle** - No duplicate code across route files  
✅ **Testable** - Can test auth logic separately from components

## Page Transitions

Add smooth transitions between routes:

```typescript
// components/layout/PageTransition.tsx
import { motion } from 'framer-motion'
import { useMatches } from '@tanstack/react-router'

export function PageTransition({ children }: { children: React.ReactNode }) {
  const matches = useMatches()
  const pathname = matches[matches.length - 1]?.pathname
  
  return (
    <motion.div
      key={pathname}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  )
}

// Use in __root.tsx
<AnimatePresence mode="wait">
  <PageTransition>
    <Outlet />
  </PageTransition>
</AnimatePresence>
```

## Error Handling

### Route-Level Errors

```typescript
// routes/trips.$tripId.tsx
export const Route = createFileRoute('/trips/$tripId')({
  component: TripDetailPage,
  errorComponent: TripErrorBoundary,
})

function TripErrorBoundary({ error }: { error: Error }) {
  return (
    <div className="p-4">
      <h1>Error loading trip</h1>
      <p>{error.message}</p>
      <Link to="/trips">Back to trips</Link>
    </div>
  )
}
```

### Not Found Routes

```typescript
// routes/__root.tsx
export const Route = createRootRoute({
  component: RootLayout,
  notFoundComponent: () => <div>Page not found</div>,
})
```

## Best Practices

✅ **DO:**
- Use file-based routing (let the plugin generate routes)
- Validate and parse params for type safety
- Use `beforeLoad` for auth checks
- Add loaders for critical data
- Use Link component for navigation (not `<a>` tags)
- Keep route components thin (delegate to feature components)

❌ **DON'T:**
- Manually define routes ( defeats the purpose!)
- Forget to handle loading states
- Put business logic in route files
- Use `window.location` for navigation
- Forget error boundaries

## Common Patterns

### Tab-Based Navigation

```typescript
// routes/trips.$tripId.tsx
export const Route = createFileRoute('/trips/$tripId')({
  component: TripDetailPage,
  validateSearch: (search) => ({
    tab: (search.tab as 'itinerary' | 'map' | 'budget') || 'itinerary',
  }),
})

function TripDetailPage() {
  const { tab } = useSearch({ from: '/trips/$tripId' })
  const navigate = useNavigate()
  
  const setTab = (newTab: string) => {
    navigate({
      to: '.', // Current route
      search: { tab: newTab },
    })
  }
  
  return (
    <Tabs value={tab} onValueChange={setTab}>
      <TabsList>
        <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
        <TabsTrigger value="map">Map</TabsTrigger>
        <TabsTrigger value="budget">Budget</TabsTrigger>
      </TabsList>
      
      <TabsContent value="itinerary">
        <TripTimeline />
      </TabsContent>
      <TabsContent value="map">
        <TripMap />
      </TabsContent>
      <TabsContent value="budget">
        <TripBudget />
      </TabsContent>
    </Tabs>
  )
}
```

### Modal Routes

```typescript
// routes/trips.$tripId.edit.tsx (modal)
export const Route = createFileRoute('/trips/$tripId/edit')({
  component: EditTripModal,
})

function EditTripModal() {
  const navigate = useNavigate()
  
  return (
    <Dialog open onOpenChange={() => navigate({ to: '..' })}>
      <DialogContent>
        <EditTripForm />
      </DialogContent>
    </Dialog>
  )
}
```

## DevTools

TanStack Router comes with devtools:

```typescript
// routes/__root.tsx
import { TanStackRouterDevtools } from '@tanstack/router-devtools'

function RootLayout() {
  return (
    <>
      <Outlet />
      <TanStackRouterDevtools position="bottom-right" />
    </>
  )
}
```

Shows:
- Current route tree
- Active routes
- Params and search values
- Navigation history

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for overall structure
- Read [STATE_MANAGEMENT.md](./STATE_MANAGEMENT.md) for Zustand patterns
- Read [DATA_FLOW.md](./DATA_FLOW.md) for data fetching
