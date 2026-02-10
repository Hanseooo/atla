# [Feature]: Landing/Hero Page for Unauthenticated Users

## Feature Summary
Create a public landing/hero page at `/` that serves as the entry point for unauthenticated users. This page will showcase the app's value proposition and provide clear CTAs to sign up or log in. The current dashboard at `/` should be moved to `/home`.

## User Story
As a **potential user visiting the site for the first time**, I want to **see a compelling hero section that explains the app's value**, so that **I'm motivated to sign up and start planning my Philippine trip**.

## Acceptance Criteria
- [ ] Landing page exists at `/` route (public, no auth required)
- [ ] Current dashboard moved to `/home` route (protected, requires auth)
- [ ] Hero section with compelling headline and subheadline about Philippine travel
- [ ] Two clear CTAs: "Get Started" (→ /signup) and "Sign In" (→ /login)
- [ ] Design is responsive and mobile-friendly
- [ ] Uses existing shadcn/ui components (Button, Card, etc.)
- [ ] Follows project's styling patterns (Tailwind CSS)
- [ ] Route guards updated: unauthenticated users see landing, authenticated see /home

## Technical Requirements

### Files to Create/Modify

**Create:**
- `src/pages/LandingPage.tsx` - Hero page component with marketing content
- `src/routes/landing.tsx` - Route wrapper for `/` (public)
- `src/routes/home.tsx` - Route wrapper for `/home` (protected, moved from index.tsx)

**Modify:**
- `src/routes/index.tsx` - Change from HomePage to LandingPage, remove auth guard
- `src/lib/auth-guards.ts` - May need optionalAuth or redirect logic update
- Update auth flow: after login/signup, redirect to `/home` instead of `/`

### Dependencies
```bash
# No new dependencies needed
# Uses existing: shadcn/ui components, Tailwind CSS, TanStack Router
```

### Route Structure
```
/          → LandingPage (public, no auth)
/home      → HomePage (protected, requires auth)
/login     → LoginPage (guest only)
/signup    → SignupPage (guest only)
```

## Architecture Notes

### Route Pattern (TanStack Router)
Follow the established Pages vs Routes pattern:

```typescript
// src/routes/landing.tsx (thin wrapper)
import { createFileRoute } from '@tanstack/react-router'
import { LandingPage } from '../pages/LandingPage'

export const Route = createFileRoute('/')({
  component: LandingRoute,
})

function LandingRoute() {
  return <LandingPage />
}
```

```typescript
// src/pages/LandingPage.tsx (full component)
export function LandingPage() {
  return (
    // Hero section, CTAs, etc.
  )
}
```

### State Management
- No server state needed (static landing page)
- No client state needed
- Navigation handled via TanStack Router's `useNavigate`

### Component Pattern
- [x] Create page component in `src/pages/LandingPage.tsx`
- [x] Create route wrapper in `src/routes/landing.tsx`
- [x] Modify existing `src/routes/index.tsx` to point to LandingPage
- [x] Create new `src/routes/home.tsx` for dashboard

## Design Specifications

### UI/UX Requirements
- [x] Responsive design (mobile-first approach)
- [x] Hero section takes full viewport height on desktop
- [x] Clear visual hierarchy (headline > subheadline > CTAs)
- [x] Accessible (semantic HTML, focus states on buttons)
- [x] Loading states not needed (static content)

### Styling
- Use Tailwind CSS utility classes
- Follow existing shadcn/ui Button component patterns
- Consistent with LoginPage/SignupPage styling (centered cards)
- Consider gradient backgrounds or Philippine imagery (designer's choice)

### Suggested Sections (flexible)
1. **Hero Section** (required)
   - Headline: "Plan Your Perfect Philippine Adventure"
   - Subheadline: "AI-powered trip planning for Palawan, Boracay, Cebu & more"
   - Two CTAs side by side: "Get Started" (primary) + "Sign In" (secondary)

2. **Optional** (if time permits)
   - Brief feature highlights (3 cards)
   - Simple footer with links

## Definition of Done
- [x] Landing page implemented at `/` route
- [x] Home dashboard moved to `/home` route
- [x] Route guards updated (auth flow redirects correctly)
- [x] Two CTAs navigate to `/login` and `/signup`
- [x] TypeScript types defined (no `any` types)
- [x] Responsive design tested (mobile, tablet, desktop)
- [x] Code follows project conventions (see ARCHITECTURE.md)
- [x] Build passes (`npm run build`)
- [x] Type check passes (`npm run typecheck`)
- [x] Self-review completed

## Additional Context

### Current Auth Flow (to be updated)
```
Current: Unauthenticated → /login
New:     Unauthenticated → / (landing)
         Authenticated   → /home
```

### Reference Files
- `src/pages/LoginPage.tsx` - Styling reference
- `src/pages/SignupPage.tsx` - Styling reference  
- `src/routes/login.tsx` - Route wrapper pattern
- `frontend/atla/docs/ARCHITECTURE.md` - Architecture patterns

### Design Inspiration (optional)
- Clean, modern SaaS landing pages
- Travel planning apps (TripIt, Wanderlog)
- Philippine tourism websites

## Related Issues
- Related to: Navigation system (future BottomNav component)
- Depends on: None (can be implemented independently)

## Estimated Effort
- [ ] Small (1-2 days) ✅
- [ ] Medium (3-5 days)
- [ ] Large (1+ weeks)

## Notes for Developer
1. This is a **public page** - no authentication required
2. Keep it **simple and fast** - minimal dependencies
3. **Design is flexible** - use your creativity for the hero section
4. **Mobile-first** - most users will see this on mobile
5. Test the **auth flow** thoroughly - make sure redirects work correctly
6. Run `npm run build` and `npm run typecheck` before submitting PR

## Questions?
- Check ARCHITECTURE.md for routing and component patterns
- Look at existing LoginPage/SignupPage for styling examples
- Ask in comments if anything is unclear
