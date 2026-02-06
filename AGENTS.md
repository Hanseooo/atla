# AGENTS.md - AI Coding Agent Instructions

This file provides context and guidelines for AI coding agents working on the Philippine AI Travel Planning application.

## Project Overview

A full-stack AI-powered travel planning app for the Philippines with a chat-first interface powered by Google Gemini.

**Tech Stack:**
- Frontend: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- Backend: FastAPI + Python 3.11+ + SQLModel (SQLAlchemy + Pydantic)
- Database: PostgreSQL via Supabase with Row Level Security (RLS)
- AI: LangChain + Google Gemini 2.5 flash-lite
- Cache: Redis via Upstash

## Build Commands

### Backend (Python/FastAPI)

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Development server
uvicorn app.main:app --reload

# Testing
pytest                    # Run all tests
pytest tests/test_specific.py  # Run single test file
pytest -k test_name      # Run specific test by name
pytest -v                # Verbose output

# Linting & Formatting
black app/               # Format Python code
ruff app/                # Lint Python code
ruff check app/          # Check only (no fix)
ruff check --fix app/    # Auto-fix issues

# Database
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head     # Apply all migrations
alembic downgrade -1     # Rollback one migration
```

### Frontend (React/TypeScript)

```bash
cd frontend

# Development
npm run dev              # Start Vite dev server

# Building
npm run build            # Production build
npm run preview          # Preview production build

# Testing
npm run test             # Run all tests
npm run test:ui          # Run tests with UI
npm run test -- --run    # Run tests once (headless)
npm run test -- MyComponent.test.tsx  # Run specific test

# Linting & Formatting
npm run lint             # Run ESLint
npm run lint -- --fix    # Auto-fix ESLint issues
npm run format           # Run Prettier
```

## Code Style Guidelines

### Python (Backend)

**Formatting (Black):**
- Line length: 88 characters
- Use double quotes for strings
- Trailing commas in multi-line structures

**Linting (Ruff):**
- Follow PEP 8 conventions
- Import sorting: standard library → third-party → local
- Type hints required for function signatures

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `TripRepository`, `UserProfile`)
- Functions/Variables: `snake_case` (e.g., `get_user_trips`, `user_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_TRIP_DAYS`)
- Private methods: `_leading_underscore`
- SQLModel models: Singular nouns (e.g., `Trip`, `Activity`)
- Repository classes: `{Model}Repository` (e.g., `TripRepository`)

**Import Structure:**
```python
# 1. Standard library
from typing import Optional, List
from datetime import datetime

# 2. Third-party
from sqlmodel import SQLModel, Field, Relationship
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local modules
from app.models.trip import Trip
from app.repositories.trip_repo import TripRepository
from app.db.session import get_session
```

**Error Handling:**
- Use custom exceptions in `app/exceptions/`
- Wrap external API calls in try/except blocks
- Log errors with context: `logger.exception("Failed to fetch place: %s", place_id)`
- Return appropriate HTTP status codes (400, 404, 500)

**Type Hints:**
- Required for all function parameters and return types
- Use `Optional[T]` for nullable types
- Use SQLModel response models for API responses

### TypeScript/React (Frontend)

**Formatting (Prettier):**
- Semicolons: true
- Single quotes: true
- Tab width: 2 spaces
- Trailing commas: es5

**Naming Conventions:**
- Components: `PascalCase` (e.g., `TripCard`, `ChatInterface`)
- Hooks: `usePascalCase` (e.g., `useAuth`, `useTrips`)
- Functions/Variables: `camelCase` (e.g., `fetchTrips`, `userId`)
- Types/Interfaces: `PascalCase` (e.g., `TripDetail`, `UserProfile`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

**File Structure:**
- Components: `src/components/{ComponentName}.tsx`
- Hooks: `src/hooks/use{HookName}.ts`
- Types: `src/types/{domain}.ts`
- Utils: `src/lib/{utility}.ts`

**Component Pattern:**
```typescript
// Props interface
interface TripCardProps {
  trip: Trip;
  onDelete?: (id: number) => void;
}

// Component
export function TripCard({ trip, onDelete }: TripCardProps) {
  // Component logic
  return (
    // JSX
  );
}
```

## Architecture Patterns

### Backend Patterns

**Repository Pattern:**
- All database access through repository classes
- Base repository in `app/repositories/base.py`
- Specific repos extend `BaseRepository[ModelType]`

**Dependency Injection:**
- Use FastAPI's `Depends()` for session, auth, etc.
- Define dependencies in `app/api/deps.py`

**SQLModel Best Practices:**
- One model per file in `app/models/`
- Use `table=True` for database tables
- Separate response models (no `table=True`) for API responses
- Use Field() for validation and constraints

**Async Pattern:**
- All database operations are async using `AsyncSession`
- Repository methods use `async def`
- Use `await` consistently

### Frontend Patterns

**Data Fetching:**
- Use React Query (TanStack Query) for server state
- Define query keys consistently: `['trips', userId]`, `['trip', tripId]`
- Use mutations for POST/PUT/DELETE operations

**State Management:**
- React Query for server state
- React Context for auth state
- useState/useReducer for local component state

**Error Handling:**
- Use React Query's error handling
- Display user-friendly error messages
- Log errors to console in development

## Security Guidelines

- Never commit `.env` files
- Use Supabase Row Level Security (RLS) policies
- Validate all user inputs with Pydantic models
- Sanitize data before rendering in UI
- Use parameterized queries (SQLModel handles this)

## API Conventions

**Backend Endpoints:**
- Use `/api/` prefix for all routes
- RESTful resource naming: `/api/trips`, `/api/trips/{id}`
- Use HTTP methods: GET, POST, PUT, DELETE
- Return consistent response structure

**Frontend API Calls:**
- Use axios or fetch with base URL from env
- Handle errors gracefully
- Use TypeScript types for API responses

## Testing Guidelines

### Python Testing
- Use pytest with pytest-asyncio for async tests
- Test files: `tests/test_{module}.py`
- Fixtures in `tests/conftest.py`
- Mock external APIs (Gemini, Brave, etc.)

### TypeScript Testing
- Use Vitest (configured with Vite)
- Test files: `{Component}.test.tsx` or `{module}.test.ts`
- Use React Testing Library for component tests
- Mock API calls with MSW (Mock Service Worker)

## Environment Variables

### Backend (.env)
```
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=...
GOOGLE_API_KEY=...
BRAVE_API_KEY=...
REDIS_URL=...
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
```

Always use `VITE_` prefix for frontend env vars to expose them to the app.

## Development Workflow

1. **Start backend**: `cd backend && uvicorn app.main:app --reload`
2. **Start frontend**: `cd frontend && npm run dev`
3. **Make changes** following style guidelines
4. **Run linting**: `ruff check app/` and `npm run lint`
5. **Run tests**: `pytest` and `npm run test`
6. **Format code**: `black app/` and `npm run format`

## Documentation References

- Architecture: See `ARCH.md` for detailed system design
- Setup: See `SETUP.md` for environment setup
- API Docs: Available at `http://localhost:8000/docs` when backend running

## Important Notes

- This project uses SQLModel which combines SQLAlchemy ORM with Pydantic validation
- All database operations are async using asyncpg
- Repository pattern is mandatory for database access
- RLS policies protect user data in Supabase
- AI features use LangChain with Google Gemini
