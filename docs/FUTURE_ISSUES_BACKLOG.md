# Future Issues Backlog (Post-Current Open Issues)

This document captures potential work items identified from the current implementation and documentation review.

- Baseline branch: `main`
- Baseline commit checked: `a122f9c`
- Existing open issues intentionally excluded: `#28`, `#29`, `#30`
- Source check included GitHub issue listing via `gh`

Use this file as a reference when creating future GitHub issues.

## Priority Legend

- `P0`: Critical product capability gap
- `P1`: Important reliability or user experience improvement
- `P2`: Quality, hardening, or maintenance improvement

---

## 1) Persist itineraries generated from chat

- Priority: `P0`
- Suggested issue title: `[Backend]: Persist chat-generated itineraries to trips tables`
- Why this matters: Itineraries are generated and returned, but not saved as durable trip records.
- Current signals:
  - `backend/app/services/chat_service.py` returns itinerary responses without repository persistence flow.
  - Trip repositories/models already exist and can support this.
- Scope:
  - Save generated itinerary output into `Trip`, `TripDay`, and `Activity` records.
  - Link persisted trip to the session/user context.
  - Return created `trip_id` and related metadata in response.
- Acceptance criteria:
  - Generated itinerary creates DB records successfully.
  - Reloading trips shows newly created trip.
  - Failure paths return clear errors and do not create partial broken data.

## 2) Add missing trips API endpoints

- Priority: `P0`
- Suggested issue title: `[Backend]: Implement /api/trips CRUD and detail endpoints`
- Why this matters: Frontend trip pages cannot be fully data-driven without trip endpoints.
- Current signals:
  - `backend/app/main.py` mounts `auth` and `chat` routers only.
  - No dedicated trips router currently exposed.
- Scope:
  - Add endpoints for list, detail, and optional create/update/delete as needed by UI.
  - Enforce per-user ownership checks.
  - Return shapes aligned with frontend route needs.
- Acceptance criteria:
  - Authenticated user can fetch their trips list and trip detail.
  - Cross-user access is denied.
  - API docs reflect new endpoints.

## 3) Connect chat API auth to real user identity

- Priority: `P1`
- Suggested issue title: `[Backend]: Wire optional auth dependency for chat endpoints`
- Why this matters: Chat sessions are not tied to authenticated users, limiting personalization and ownership.
- Current signals:
  - `backend/app/api/chat.py` includes `get_current_user_optional()` placeholder returning `None`.
- Scope:
  - Replace placeholder with real optional auth dependency.
  - Pass authenticated `user_id` into chat service flows.
  - Ensure anonymous usage still works where intended.
- Acceptance criteria:
  - Authenticated requests carry user context end-to-end.
  - Unauthenticated requests still function according to product rules.
  - Tests cover both authenticated and anonymous paths.

## 4) Replace in-memory chat sessions with durable session storage

- Priority: `P1`
- Suggested issue title: `[Backend]: Add durable chat session storage (Redis-backed)`
- Why this matters: In-memory sessions are lost on restart and are not multi-instance safe.
- Current signals:
  - `backend/app/services/chat_service.py` stores sessions in class-level `_sessions` dict.
- Scope:
  - Introduce Redis-backed session read/write with TTL policy.
  - Keep session schema compatible with existing chat flow.
  - Add graceful handling for expired/missing sessions.
- Acceptance criteria:
  - Session survives process restart (with Redis retained state).
  - Multiple backend instances can access the same session state.
  - Expired sessions produce user-friendly recovery messages.

## 5) Wire frontend pages to real backend data/actions

- Priority: `P1`
- Suggested issue title: `[Frontend]: Replace placeholder pages with data-driven implementations`
- Why this matters: Several pages are currently scaffold-level and do not execute expected user tasks.
- Current signals:
  - `frontend/atla/src/pages/HomePage.tsx`
  - `frontend/atla/src/pages/TripsPage.tsx`
  - `frontend/atla/src/pages/ExplorePage.tsx`
  - `frontend/atla/src/pages/ProfilePage.tsx`
- Scope:
  - Connect pages to API hooks/queries.
  - Implement primary actions (view trips, navigate to trip detail, profile updates, explore results).
  - Add loading/empty/error states.
- Acceptance criteria:
  - Pages render live data from API.
  - Core actions are functional and navigable.
  - Error and empty states are handled consistently.

## 6) Align documentation with current implementation

- Priority: `P2`
- Suggested issue title: `[Docs]: Sync project documentation with current app implementation`
- Why this matters: Outdated docs create onboarding and planning confusion.
- Current signals:
  - `frontend/atla/README.md` still contains default Vite template content.
  - Architecture docs include planned components/flows not fully implemented.
- Scope:
  - Update frontend README to real app setup/commands/feature status.
  - Mark planned vs implemented sections clearly in architecture docs.
  - Add a short "current state" snapshot section.
- Acceptance criteria:
  - New contributors can run app using docs without assumptions.
  - Docs explicitly separate implemented features from roadmap items.

## 7) Add API protection and observability hardening

- Priority: `P2`
- Suggested issue title: `[Backend]: Add rate limiting and structured observability baseline`
- Why this matters: Production readiness requires abuse protection and better runtime visibility.
- Current signals:
  - No visible app-level rate limiter in backend API layer.
  - Monitoring/structured logging items remain open in planning docs.
- Scope:
  - Add per-route or per-user rate limiting strategy.
  - Add structured request/response logging with correlation IDs.
  - Add basic service metrics and error counters.
- Acceptance criteria:
  - High-volume request bursts are throttled predictably.
  - Logs are structured and traceable per request.
  - Basic health and error trend monitoring is available.

---

## Suggested Issue Creation Order

1. Persist chat-generated itineraries
2. Add trips API endpoints
3. Wire chat auth to real user identity
4. Move chat sessions to Redis
5. Wire frontend pages to real data
6. Sync docs to implementation
7. Add rate limiting and observability

## Notes for Future Issue Authors

- Keep issues focused on one concern.
- Include concrete file references and acceptance criteria.
- Link dependencies between issues when sequencing is required.
- Prefer opening backend enabler issues before frontend integration issues.
