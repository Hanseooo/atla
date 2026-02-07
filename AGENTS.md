# AGENTS.md - AI Coding Agent Instructions

Philippine AI Travel Planning app - full-stack with React frontend and FastAPI backend.

**Tech Stack:**
- Frontend: React 19 + TypeScript + Vite + Tailwind CSS v4 + TanStack Router/Query + Zustand
- Backend: FastAPI + Python 3.11+ + SQLModel + asyncpg + PostgreSQL (Supabase)
- AI: LangChain + Google Gemini 2.5 flash-lite
- Cache: Redis via Upstash

## Build Commands

### Backend (Python/FastAPI)

```bash
cd backend && source venv/bin/activate  # Windows: venv\Scripts\activate

# Development
uvicorn app.main:app --reload

# Testing
pytest                           # Run all tests
pytest tests/test_specific.py   # Run single test file
pytest -k test_name            # Run specific test by name
pytest -v                      # Verbose output

# Linting & Formatting
black app/                     # Format Python code
ruff check app/                # Check only
ruff check --fix app/          # Auto-fix issues

# Database
alembic revision --autogenerate -m "Description"
alembic upgrade head           # Apply migrations
alembic downgrade -1           # Rollback one migration
```

### Frontend (React/TypeScript)

```bash
cd frontend/atla

# Development
npm run dev                    # Start Vite dev server
npm run preview               # Preview production build
npm run build                 # Production build

# Testing (Vitest not yet configured - add with: npm install -D vitest @testing-library/react @testing-library/jest-dom)
# Then use: npx vitest run src/components/MyComponent.test.tsx

# Linting
npm run lint                  # Run ESLint
npm run lint -- --fix         # Auto-fix ESLint issues
```

## Code Style Guidelines

### Python (Backend)

**Formatting (Black):** Line length 88, Python 3.11+, double quotes, trailing commas.

**Linting (Ruff):** PEP 8, import order (stdlib → third-party → local), rules: E, W, F, I, N, UP.

**Naming:** Classes `PascalCase`, functions/variables `snake_case`, constants `UPPER_SNAKE_CASE`, private `_leading_underscore`, models singular (`Trip`), repos `{Model}Repository`.

**Imports:**
```python
# 1. Standard library
from typing import Optional, List
from datetime import datetime

# 2. Third-party
from sqlmodel import SQLModel, Field
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local modules (known-first-party: app)
from app.models.trip import Trip
from app.repositories.trip_repo import TripRepository
```

**Types:** Required for all params/returns. Use `Optional[T]` for nullable, SQLModel for responses, `Generic[ModelType]` for repos.

**Errors:** Use `app/exceptions/`, wrap external APIs, log with context: `logger.exception("Failed: %s", entity_id)`, return proper HTTP codes (400, 404, 500, 503).

### TypeScript/React (Frontend)

**Formatting:** ESLint/TypeScript, semicolons true, single quotes, 2-space tabs.

**Naming:** Components `PascalCase` (`TripCard`), hooks `usePascalCase`, functions/variables `camelCase`, types `PascalCase`, constants `UPPER_SNAKE_CASE`.

**File Structure:**
- Routes: `src/routes/{route}.tsx` (TanStack file-based routing)
- Components: `src/components/{Name}.tsx`
- Hooks: `src/hooks/use{Name}.ts`
- Utils: `src/lib/{utility}.ts`

**Component Pattern:**
```typescript
interface TripCardProps { trip: Trip; onDelete?: (id: number) => void; }

export function TripCard({ trip, onDelete }: TripCardProps) {
  return (/* JSX */);
}

// TanStack Router
defineFileRoute('/trips/$tripId')({
  component: TripDetailPage,
  beforeLoad: requireAuth,
})
```

**Path Aliases:** `@/` maps to `./src/`. Use: `import { Button } from '@/components/ui/button'`

## Architecture Patterns

### Backend

**Repository Pattern:** All DB access through repos. Base: `app/repositories/base.py` with `BaseRepository[ModelType]`. Specific repos extend base.

**Dependency Injection:** Use FastAPI `Depends()` for session/auth. Define in `app/api/deps.py`.

**SQLModel:** One model per file in `app/models/`. Use `table=True` for DB tables. Separate response models (no `table=True`). Use `Field()` for validation. Use `sa_column=Column(JSONB)` for JSON.

**Async:** All DB ops async via `AsyncSession`. Repository methods use `async def`.

### Frontend

**Data Fetching:** Use TanStack Query for server state. Query keys: `['trips', userId]`, `['trip', tripId]`. Mutations for POST/PUT/DELETE.

**State:** React Query (server), Zustand (global auth/UI), useState/useReducer (local).

**Routing:** File-based in `src/routes/`. Files match URL: `trips.$tripId.tsx` → `/trips/123`. Use `beforeLoad` for auth. Index routes: `index.tsx`, `trips.index.tsx`.

**Errors:** React Query error handling + error boundaries. User-friendly messages. Log in dev.

## Security

- Never commit `.env` files
- Use Supabase Row Level Security (RLS)
- Validate inputs with Pydantic
- Sanitize UI rendering
- Use parameterized queries (SQLModel handles this)

## API Conventions

**Backend:** `/api/` prefix. RESTful: `/api/trips`, `/api/trips/{id}`. Methods: GET, POST, PUT, DELETE, PATCH.

**Frontend:** Use axios. Base URL from `VITE_API_URL`. Handle errors with React Query.

## Environment Variables

**Backend (.env):** `ENVIRONMENT`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GOOGLE_API_KEY`, `BRAVE_API_KEY`, `REDIS_URL`

**Frontend (.env):** `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (always use `VITE_` prefix)

## Development Workflow

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend/atla && npm run dev`
3. Make changes following style guidelines
4. Run linting: `ruff check app/` and `npm run lint`
5. Run tests: `pytest` (backend configured)
6. Format: `black app/`

## Important Notes

- SQLModel = SQLAlchemy ORM + Pydantic validation
- All DB ops async via asyncpg
- Repository pattern mandatory for DB access
- RLS policies protect user data
- AI uses LangChain + Google Gemini
- Tailwind CSS v4 with `@tailwindcss/vite`
- TanStack Router: file-based routing, create files in `src/routes/`
