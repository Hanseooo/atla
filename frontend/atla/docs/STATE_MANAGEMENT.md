# State Management Guide

## Overview

We use a **two-layer state management approach**:

```
┌─────────────────────────────────────────┐
│         STATE MANAGEMENT                │
├─────────────────────────────────────────┤
│                                         │
│  🌐 SERVER STATE (TanStack Query)      │
│  ─────────────────────────────────────  │
│  • Trips, Places, User data            │
│  • Remote data that needs caching      │
│  • Shared across components            │
│  • Automatic syncing with backend      │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  💻 CLIENT STATE (Zustand)             │
│  ─────────────────────────────────────  │
│  • Auth session                        │
│  • UI state (nav visibility)           │
│  • Temporary data (chat messages)      │
│  • Local preferences                   │
│                                         │
└─────────────────────────────────────────┘
```

## When to Use What?

| Use Case | Solution | Example |
|----------|----------|---------|
| Data from API | TanStack Query | List of trips, place details |
| User authentication | Zustand | Current user, JWT token |
| Form inputs | useState | Login form, search input |
| UI visibility | Zustand | Bottom nav visible/hidden |
| Temporary messages | Zustand | Chat conversation |
| Shared component state | Zustand | Selected filters |

## Zustand Stores

### 1. Auth Store

Manages authentication state and user session.

```typescript
// stores/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabase } from '../lib/supabase'
import type { User } from '@supabase/supabase-js'

interface AuthState {
  // State
  user: User | null
  session: any | null
  isLoading: boolean
  
  // Actions
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, username: string) => Promise<void>
  signOut: () => Promise<void>
  setUser: (user: User | null) => void
  setSession: (session: any | null) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      session: null,
      isLoading: false,
      
      // Actions
      signIn: async (email, password) => {
        set({ isLoading: true })
        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
          })
          
          if (error) throw error
          
          set({ 
            user: data.user, 
            session: data.session,
            isLoading: false 
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      signUp: async (email, password, username) => {
        set({ isLoading: true })
        try {
          const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
              data: { username },
            },
          })
          
          if (error) throw error
          
          set({ 
            user: data.user, 
            session: data.session,
            isLoading: false 
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },
      
      signOut: async () => {
        await supabase.auth.signOut()
        set({ user: null, session: null })
      },
      
      setUser: (user) => set({ user }),
      setSession: (session) => set({ session }),
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({ 
        // Only persist session, not user (get from session)
        session: state.session 
      }),
    }
  )
)
```

**Usage:**
```typescript
function LoginPage() {
  const { signIn, isLoading } = useAuthStore()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await signIn(email, password)
  }
  
  return <form onSubmit={handleSubmit}>...</form>
}
```

### 2. Chat Store

Manages chat conversation state and AI intent.

```typescript
// stores/chatStore.ts
import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface TravelIntent {
  destination?: string
  days?: number
  budget?: 'low' | 'mid' | 'luxury'
  travel_style?: string[]
  companions?: 'solo' | 'couple' | 'friends' | 'family'
  missing_info?: string[]
}

interface ChatState {
  // State
  messages: Message[]
  intent: TravelIntent | null
  isTyping: boolean
  currentTripId: number | null
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  setIntent: (intent: TravelIntent | null) => void
  setIsTyping: (isTyping: boolean) => void
  setCurrentTripId: (tripId: number | null) => void
  clearChat: () => void
}

export const useChatStore = create<ChatState>()((set) => ({
  // Initial state
  messages: [],
  intent: null,
  isTyping: false,
  currentTripId: null,
  
  // Actions
  addMessage: (message) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...message,
        id: crypto.randomUUID(),
        timestamp: new Date(),
      },
    ],
  })),
  
  setIntent: (intent) => set({ intent }),
  
  setIsTyping: (isTyping) => set({ isTyping }),
  
  setCurrentTripId: (tripId) => set({ currentTripId: tripId }),
  
  clearChat: () => set({ 
    messages: [], 
    intent: null, 
    currentTripId: null 
  }),
}))
```

**Usage:**
```typescript
function ChatInterface() {
  const { messages, addMessage, intent, isTyping } = useChatStore()
  
  const handleSend = (content: string) => {
    addMessage({ role: 'user', content })
    // Send to API, get response...
  }
  
  return (
    <div>
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isTyping && <TypingIndicator />}
    </div>
  )
}
```

### 3. UI Store

Manages UI state like navigation visibility and preferences.

```typescript
// stores/uiStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  // State
  isBottomNavVisible: boolean
  theme: 'light' | 'dark' | 'system'
  sidebarCollapsed: boolean
  
  // Actions
  setBottomNavVisible: (visible: boolean) => void
  toggleBottomNav: () => void
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Initial state
      isBottomNavVisible: true,
      theme: 'system',
      sidebarCollapsed: false,
      
      // Actions
      setBottomNavVisible: (visible) => set({ 
        isBottomNavVisible: visible 
      }),
      
      toggleBottomNav: () => set((state) => ({ 
        isBottomNavVisible: !state.isBottomNavVisible 
      })),
      
      setTheme: (theme) => set({ theme }),
      
      toggleSidebar: () => set((state) => ({ 
        sidebarCollapsed: !state.sidebarCollapsed 
      })),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({ 
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        // Don't persist nav visibility (reset on reload)
      }),
    }
  )
)
```

**Usage:**
```typescript
function BottomNav() {
  const { isBottomNavVisible } = useUIStore()
  
  return (
    <motion.nav
      initial={false}
      animate={{ 
        y: isBottomNavVisible ? 0 : 100 
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Nav content */}
    </motion.nav>
  )
}
```

## Store Best Practices

### 1. Keep Stores Focused

❌ **Don't:** One giant store
```typescript
// BAD
const useStore = create(() => ({
  user: null,      // Auth
  messages: [],    // Chat
  isNavVisible: true, // UI
  trips: [],       // Server (use TanStack Query!)
}))
```

✅ **Do:** Separate by concern
```typescript
// GOOD
const useAuthStore = create(() => ({ user: null }))
const useChatStore = create(() => ({ messages: [] }))
const useUIStore = create(() => ({ isNavVisible: true }))
```

### 2. Use Selectors to Prevent Re-renders

❌ **Don't:** Subscribe to entire store
```typescript
// BAD - Component re-renders when ANY state changes
const store = useAuthStore()
return <div>{store.user?.name}</div>
```

✅ **Do:** Subscribe to specific slices
```typescript
// GOOD - Only re-renders when user changes
const user = useAuthStore(state => state.user)
return <div>{user?.name}</div>
```

### 3. Use Persist for Important Data

```typescript
import { persist } from 'zustand/middleware'

const useStore = create(
  persist(
    (set) => ({ ... }),
    {
      name: 'my-storage',
      partialize: (state) => ({ 
        // Only persist these fields
        theme: state.theme,
        preferences: state.preferences,
      }),
    }
  )
)
```

### 4. Separate Actions from State

```typescript
interface StoreState {
  count: number
  increment: () => void
  decrement: () => void
}

const useStore = create<StoreState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}))
```

### 5. Use Immer for Complex Updates

```typescript
import { produce } from 'immer'

const useStore = create((set) => ({
  nested: { deep: { value: 0 } },
  
  updateDeep: (value) => set(produce((draft) => {
    draft.nested.deep.value = value
  })),
}))
```

## Integration with React Query

### Syncing Auth with React Query

```typescript
// hooks/useAuth.ts
import { useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useQueryClient } from '@tanstack/react-query'

export function useAuth() {
  const { user, setUser } = useAuthStore()
  const queryClient = useQueryClient()
  
  useEffect(() => {
    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setUser(session?.user ?? null)
        
        // Clear query cache on sign out
        if (event === 'SIGNED_OUT') {
          queryClient.clear()
        }
      }
    )
    
    return () => subscription.unsubscribe()
  }, [])
  
  return { user }
}
```

### Accessing Store in React Query Hooks

```typescript
// hooks/useTrips.ts
export const useTrips = () => {
  const { user } = useAuthStore()
  
  return useQuery({
    queryKey: ['trips', user?.id],
    queryFn: () => api.get('/api/trips'),
    enabled: !!user, // Only fetch if logged in
  })
}
```

## Advanced Patterns

### Computed Values

```typescript
const useCartStore = create((set, get) => ({
  items: [],
  
  // Computed value
  get totalPrice() {
    return get().items.reduce((sum, item) => sum + item.price, 0)
  },
  
  // Or use selector
  getItemCount: () => get().items.length,
}))

// Usage
const total = useCartStore(state => state.totalPrice)
const count = useCartStore(state => state.getItemCount())
```

### Async Actions

```typescript
const useStore = create((set) => ({
  data: null,
  isLoading: false,
  error: null,
  
  fetchData: async () => {
    set({ isLoading: true, error: null })
    try {
      const data = await api.get('/data')
      set({ data, isLoading: false })
    } catch (error) {
      set({ error, isLoading: false })
    }
  },
}))
```

### Store Composition

```typescript
// Base store creator
const createBaseStore = (initialState) => (set, get) => ({
  ...initialState,
  reset: () => set(initialState),
})

// Extended store
const useFeatureStore = create((set, get) => ({
  ...createBaseStore({ count: 0 })(set, get),
  double: () => set((state) => ({ count: state.count * 2 })),
}))
```

## DevTools

Enable Zustand devtools for debugging:

```typescript
import { devtools } from 'zustand/middleware'

const useStore = create(
  devtools(
    (set) => ({ ... }),
    { name: 'MyStore' }
  )
)
```

Shows in Redux DevTools:
- State changes
- Action history
- Time-travel debugging

## Common Pitfalls

❌ **Don't:**
- Store server data in Zustand (use React Query)
- Subscribe to entire store (causes re-renders)
- Mutate state directly (always use set)
- Forget to handle cleanup in effects

✅ **Do:**
- Use selectors for granular subscriptions
- Separate stores by domain
- Persist only necessary data
- Use TypeScript for type safety

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for overall structure
- Read [DATA_FLOW.md](./DATA_FLOW.md) for server state patterns
- Read [ROUTING.md](./ROUTING.md) for navigation
