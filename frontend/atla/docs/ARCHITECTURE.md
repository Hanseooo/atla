# Frontend Architecture Overview

## The Big Picture

Think of our frontend like a **movie theater experience**:

```
┌─────────────────────────────────────────────────────────────┐
│                  PHILIPPINE TRAVEL APP UI                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER (Moviegoer)                                           │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                            │
│  │   Router    │  ← Ticket Booth (TanStack Router)          │
│  │   (Routes)  │     Decides which "screen" to show         │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │   Pages     │  ← Movie Screens (Route Components)        │
│  │   (Routes/) │     Chat, Trips, Explore, Profile          │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │ Components  │  ← Actors & Props (React Components)       │
│  │(components/)│     Buttons, Cards, Maps, Chat UI          │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │    Hooks    │  ← Scripts (Custom React Hooks)            │
│  │   (hooks/)  │     useTrips, useAuth, usePlaces           │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │Data & State │  ← Film Archives (TanStack Query +         │
│  │ (lib/,stores)│    Zustand)                               │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │    API      │  ← Projection Room (Axios + Supabase)      │
│  │   (lib/)    │     Fetches data from backend              │
│  └─────────────┘                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## User Flow Through the App

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Login   │────▶│   Home   │────▶│   Chat   │────▶│  Detail  │
│  Screen  │     │Dashboard │     │  Screen  │     │  Screen  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                │                  │
                       │  "My Trips"    │"Plan Palawan"   │
                       │                │                  │
                       ▼                ▼                  ▼
                ┌──────────┐     ┌──────────┐     ┌──────────┐
                │  Trips   │     │  Intent  │     │  Tabs:   │
                │   List   │     │Extraction│     │Itinerary │
                └──────────┘     └──────────┘     │   Map    │
                                                  │  Budget  │
                                                  └──────────┘
```

**Flow Description:**
1. **Login/Signup** → New users create account, existing users sign in
2. **Home/Dashboard** (`/`) - Trip dashboard showing user's plans
3. **Chat** (`/chat`) - AI-powered trip planning interface
4. **Trip Detail** (`/trips/:id`) - View saved trip with itinerary, map, budget tabs
5. **Trips List** (`/trips`) - Browse all saved trips
6. **Explore** (`/explore`) - Discover new places
7. **Profile** (`/profile`) - User settings and preferences

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | React 19 | UI library with concurrent features |
| **Build Tool** | Vite | Fast development and building |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | shadcn/ui | Accessible UI components |
| **Routing** | TanStack Router | Type-safe file-based routing |
| **State (Server)** | TanStack Query | Server state management |
| **State (Client)** | Zustand | Client state management |
| **Animations** | Framer Motion | Smooth transitions and gestures |
| **Maps** | MapCN (MapLibre) | Philippine-focused maps |
| **Auth** | Supabase Auth | Authentication & authorization |
| **HTTP Client** | Axios | API requests with interceptors |

## Directory Structure

```
frontend/atla/src/
│
├── routes/                    # 🎬 Movie Screens (Pages)
│   ├── __root.tsx            # Root layout with providers
│   ├── index.tsx             # / - Home (Trip Dashboard)
│   ├── chat.tsx              # /chat - AI trip planning
│   ├── trips.index.tsx       # /trips - My trips list
│   ├── trips.$tripId.tsx     # /trips/123 - Trip detail
│   ├── explore.index.tsx     # /explore - Browse places
│   ├── profile.index.tsx     # /profile - User settings
│   ├── login.tsx             # /login - Authentication
│   └── signup.tsx            # /signup - Create account
│
├── components/               # 🎭 Actors & Props
│   ├── ui/                  # shadcn components (direct import)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── dialog.tsx
│   │
│   ├── layout/              # Layout components
│   │   ├── BottomNav.tsx    # Animated bottom navigation
│   │   └── PageTransition.tsx # Route transition wrapper
│   │
│   ├── chat/                # Chat feature
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   └── ChatInput.tsx
│   │
│   ├── trips/               # Trip feature
│   │   ├── TripCard.tsx
│   │   ├── TripDetail.tsx
│   │   ├── TripTimeline.tsx
│   │   ├── TripMap.tsx
│   │   └── TripBudget.tsx
│   │
│   └── places/              # Places feature
│       ├── PlaceCard.tsx
│       └── PlaceDetail.tsx
│
├── hooks/                    # 📝 Scripts (Custom Hooks)
│   ├── useAuth.ts           # Authentication operations
│   ├── useTrips.ts          # Trip CRUD with TanStack Query
│   ├── usePlaces.ts         # Place search & details
│   ├── useChat.ts           # Chat with AI
│   └── useScrollDirection.ts # Navigation visibility
│
├── lib/                      # 🔧 Utilities & Configuration
│   ├── api.ts               # Axios instance with interceptors
│   ├── auth-guards.ts       # Centralized auth guard functions
│   ├── query-client.ts      # TanStack Query configuration
│   ├── supabase.ts          # Supabase client
│   └── utils.ts             # Helper functions
│
├── stores/                   # 🗃️ Client State (Zustand)
│   ├── authStore.ts         # Auth state
│   ├── chatStore.ts         # Chat messages & intent
│   └── uiStore.ts           # UI state (nav visibility)
│
└── types/                    # 📋 TypeScript Definitions
    ├── trip.ts
    ├── place.ts
    ├── chat.ts
    └── user.ts
```

## Key Architectural Decisions

### 1. File-Based Routing

**Why TanStack Router with file-based routing?**

- **Type Safety**: Routes are automatically typed
- **Code Splitting**: Each route is its own bundle
- **Convention over Configuration**: File structure = URL structure
- **Nested Layouts**: Easy layout composition

**Route Conventions:**
```
File Name              →  URL Path
─────────────────────────────────────
index.tsx              →  /
trips.index.tsx        →  /trips
trips.$tripId.tsx      →  /trips/123 (dynamic)
explore.index.tsx      →  /explore
login.tsx              →  /login
(underscore prefix)    →  No layout (auth pages)
```

### 2. State Management Strategy

**Two-Layer Approach:**

```
┌─────────────────────────────────────────┐
│         STATE MANAGEMENT                │
├─────────────────────────────────────────┤
│                                         │
│  SERVER STATE (TanStack Query)         │
│  ├── Trips list                        │
│  ├── Trip details                      │
│  ├── Places                            │
│  └── User profile                      │
│                                         │
│  Features:                             │
│  ✓ Caching                             │
│  ✓ Background refetching               │
│  ✓ Optimistic updates                  │
│  ✓ Stale-while-revalidate              │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  CLIENT STATE (Zustand)                │
│  ├── Auth session                      │
│  ├── Chat messages (temporary)         │
│  ├── Navigation visibility             │
│  └── UI preferences                    │
│                                         │
│  Features:                             │
│  ✓ Simple API                          │
│  ✓ No re-render issues                 │
│  ✓ Persist to localStorage             │
│                                         │
└─────────────────────────────────────────┘
```

**When to use which:**
- **TanStack Query**: Data from API, needs caching, shared across components
- **Zustand**: UI state, auth tokens, temporary data, component-local state

### 3. Data Fetching Strategy

**No Waterfalls Pattern:**

```typescript
// ❌ BAD - Sequential (slow)
const trip = await fetchTrip(id)
const days = await fetchTripDays(trip.id)
const activities = await fetchActivities(days[0].id)

// ✅ GOOD - Single nested request (fast)
const trip = await api.get(`/api/trips/${id}`)
// Returns: { trip, trip_days: [{ activities: [...] }] }
```

**Why this matters:**
- Faster initial load
- Simpler code
- Better user experience
- Reduced server load

### 4. Authentication & Route Guards

**Centralized Auth Guards:**

We use centralized auth guard functions in `src/lib/auth-guards.ts` to handle authentication consistently across all routes.

```typescript
// src/lib/auth-guards.ts
export async function requireAuth({ location }) {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) {
    throw redirect({
      to: '/login',
      search: { redirect: location.href },
    })
  }
}

export async function requireGuest() {
  const { data: { session } } = await supabase.auth.getSession()
  if (session) {
    throw redirect({ to: '/' })
  }
}
```

**Usage in routes:**
```typescript
// Protected route
export const Route = createFileRoute('/trips')({
  component: TripsPage,
  beforeLoad: requireAuth, // One line protection
})

// Guest-only route
export const Route = createFileRoute('/login')({
  component: LoginPage,
  beforeLoad: requireGuest,
})
```

**Protected Routes:**
- `/` - Home (Trip Dashboard)
- `/trips` - My trips
- `/trips/:tripId` - Trip detail
- `/explore` - Browse places
- `/profile` - User settings
- `/chat` - AI chat

**Guest-Only Routes:**
- `/login` - Sign in
- `/signup` - Create account

### 5. Navigation Pattern

**Bottom Tab Bar (Hide on Scroll):**

```
┌─────────────────────────────┐
│         [Chat]              │  ← Full-width chat page
│                             │
│                             │
│                             │
├─────────────────────────────┤
│ 🗨️  🗺️  🔍  👤             │  ← Bottom nav (hides on scroll down)
└─────────────────────────────┘
```

**Behavior:**
- Hide when scrolling down (more content visible)
- Show when scrolling up (easy access)
- Smooth animation with Framer Motion
- 4 tabs: Chat, Trips, Explore, Profile

### 5. Chat-First Interface

**Purpose:** Natural language trip planning powered by AI

**Flow:**
1. User types: "I want to visit Palawan for 3 days"
2. AI extracts intent: `{ destination: "Palawan", days: 3 }`
3. AI asks clarifying questions if needed
4. User provides details: budget, travel style, companions
5. AI generates itinerary preview
6. User saves → Creates trip → Redirects to detail

**Key Points:**
- Messages reset on page refresh (temporary)
- Intent stored in Zustand during conversation
- Persistent trips saved to backend

## Component Hierarchy

```
<StrictMode>
  <QueryClientProvider>
    <RouterProvider>
      <RootLayout>           ← __root.tsx
        <PageTransition>     ← Framer Motion wrapper
          <RouteComponent>   ← Current page (index.tsx, trips.index.tsx, etc.)
            <Layout/>        ← Page-specific layout
              <Components/>  ← Feature components
                <UI/>        ← shadcn components
          </RouteComponent>
        </PageTransition>
        <BottomNav/>         ← Animated bottom navigation
      </RootLayout>
    </RouterProvider>
  </QueryClientProvider>
</StrictMode>
```

## Authentication Flow

```
┌────────────┐      ┌────────────┐      ┌────────────┐
│   Login    │─────▶│  Supabase  │─────▶│   JWT      │
│   Page     │      │   Auth     │      │  Token     │
└────────────┘      └────────────┘      └────────────┘
                                               │
                                               │ Stored in
                                               │ memory
                                               ▼
┌────────────┐      ┌────────────┐      ┌────────────┐
│ Protected  │◀─────│   Axios    │◀─────│  Request   │
│   Route    │      │Interceptor │      │  Header    │
└────────────┘      └────────────┘      └────────────┘
```

**Implementation:**
- Supabase Auth handles email/password (Google coming soon)
- JWT token attached to all API requests via Axios interceptor
- Route guards check auth before loading protected pages
- Unauthenticated users redirected to `/login`

## Performance Optimizations

### 1. Code Splitting
- Each route is automatically code-split by TanStack Router
- Heavy components (maps) lazy-loaded
- shadcn components imported directly (not barrel exports)

### 2. Caching Strategy
```typescript
// Trips - cache for 5 minutes (don't change often)
staleTime: 1000 * 60 * 5

// Chat - always fresh
staleTime: 0

// Places - cache for 1 minute
staleTime: 1000 * 60
```

### 3. Re-render Optimization
- Zustand stores split by concern (auth, chat, UI)
- Components subscribe only to needed state slices
- React.memo for expensive components
- useMemo for derived data

### 4. Animation Performance
- Framer Motion uses GPU acceleration
- Animate `transform` and `opacity` only
- `layout` prop for smooth layout transitions
- Reduced motion support for accessibility

## Best Practices

### 1. Type Safety
- All API responses typed
- Route params typed automatically
- Zustand stores fully typed
- No `any` types in production code

### 2. Error Handling
- API errors caught in hooks
- Error boundaries for route errors
- Toast notifications for user feedback
- Graceful fallbacks (empty states)

### 3. Accessibility
- Semantic HTML
- Keyboard navigation support
- Focus management in modals
- ARIA labels on interactive elements
- Color contrast compliance

### 4. Mobile-First
- Touch-friendly tap targets (min 44px)
- Bottom navigation for thumb reach
- Swipe gestures where appropriate
- Responsive breakpoints
- Safe area insets for notches

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   Navigate to `http://localhost:5173`

## Next Steps

- Read [DATA_FLOW.md](./DATA_FLOW.md) for TanStack Query patterns
- Read [ROUTING.md](./ROUTING.md) for routing conventions
- Read [STATE_MANAGEMENT.md](./STATE_MANAGEMENT.md) for Zustand patterns

---

**Questions?** Check the specific guides above or look at example implementations in `src/`.
