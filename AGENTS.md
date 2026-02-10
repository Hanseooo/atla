# AGENTS.md - AI Coding Agent Instructions

Atla - A full-stack Philippine AI Travel Planning app with React frontend and FastAPI backend.

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

---

## AI Agent Guidelines

### Decision Making Protocol

AI agents must follow this protocol when working on the codebase:

**✅ Safe to Proceed (No Permission Needed):**
- Creating new files and components
- Code refactoring and cleanup
- Documentation updates
- Adding tests
- UI/UX improvements within existing patterns
- Bug fixes with clear solutions

**❌ Must Ask User First:**
- Architecture changes or pattern modifications
- Breaking changes to existing APIs
- Adding new dependencies (npm/pip packages)
- Database schema changes
- Removing existing features
- Changes to authentication/authorization logic
- Production deployment steps

**❌ User Handles (Never Do These):**
- Git operations (merge, rebase, force push)
- Resolving merge conflicts
- Production deployments
- Direct commits to `main` branch
- Rewriting git history

### Communication Guidelines

**When to Ask Questions:**
- Requirements are ambiguous or unclear
- Multiple valid approaches exist (present options with trade-offs)
- Unfamiliar with a specific pattern or convention
- Encounter unexpected errors or edge cases
- Need access to credentials or environment variables

**When to Proceed:**
- Task is clearly defined and within scope
- Following established patterns from documentation
- Changes are isolated and reversible
- No breaking changes introduced

**Stopping Points:**
- Always stop and ask before proceeding if uncertain
- Never assume user wants breaking changes
- Never push to remote branches without explicit permission
- Never run destructive commands (drop database, delete migrations, etc.)

### Branch Naming for AI Tasks

When AI agents create branches, use this naming convention:

```
feat/ai-{description}       # New features
fix/ai-{description}        # Bug fixes
docs/ai-{description}       # Documentation updates
chore/ai-{description}      # Maintenance tasks
refactor/ai-{description}   # Code refactoring
test/ai-{description}       # Adding tests
```

**Examples:**
- `feat/ai-landing-page`
- `fix/ai-login-redirect`
- `docs/ai-api-endpoints`
- `chore/ai-update-dependencies`

### Commit Message Convention

AI agents must follow **Conventional Commits** format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring without behavior changes
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, maintenance

**Scopes (optional but recommended):**
- `frontend`: React/TypeScript code
- `backend`: Python/FastAPI code
- `api`: API endpoints
- `db`: Database models/migrations
- `auth`: Authentication-related
- `ui`: UI components

**Examples:**
```bash
feat(frontend): add user authentication
fix(backend): resolve login redirect bug
docs(api): update swagger documentation
refactor(frontend): simplify trip card component
test(backend): add unit tests for auth service
chore(deps): update tanstack router to v1.20
```

### Error Handling for AI Agents

**When Build/Type Check Fails:**
1. Read error messages carefully
2. Identify root cause
3. Fix all errors systematically
4. Run checks again: `npm run typecheck` (frontend) or check Python syntax (backend)
5. Only ask user if stuck after 3+ attempts

**When Tests Fail:**
1. Read test output
2. Identify failing test cases
3. Fix the underlying issue (not the test)
4. Run tests again
5. Ask user if test logic itself is unclear

**When Conflicts Arise:**
1. Stop immediately
2. Notify user about the conflict
3. Let user resolve it (don't attempt auto-resolution)
4. Wait for user guidance before continuing

### Code Quality Checklist

Before indicating task completion, AI agents must verify:

**Frontend:**
- [ ] TypeScript compiles without errors (`npm run typecheck`)
- [ ] Build succeeds (`npm run build`)
- [ ] No `any` types used (unless absolutely necessary)
- [ ] Proper error handling implemented
- [ ] Components follow existing patterns
- [ ] Path aliases used (`@/` instead of relative paths)

**Backend:**
- [ ] Python syntax is valid
- [ ] No obvious runtime errors
- [ ] Type hints included
- [ ] Proper error handling with appropriate HTTP status codes
- [ ] Follows repository pattern

**Both:**
- [ ] Follows project conventions (see ARCHITECTURE.md)
- [ ] No secrets or credentials in code
- [ ] Documentation updated if needed
- [ ] Self-review completed

### File Operations

**Creating New Files:**
- Always check if similar files exist (follow existing patterns)
- Use correct file naming conventions
- Place in appropriate directories
- Update barrel exports if applicable

**Modifying Existing Files:**
- Read file first to understand current implementation
- Preserve existing functionality unless instructed otherwise
- Follow existing code style (don't mix patterns)
- Check for dependencies on the code being modified

**Deleting Files:**
- Always ask before deleting
- Check for references/imports in other files
- Update imports in dependent files

### Testing Strategy

**Manual Testing:**
- Describe what was tested
- Include edge cases considered
- Note any manual verification steps

**Automated Testing:**
- Add tests for new features when test framework is configured
- Ensure existing tests still pass
- Don't remove tests without explicit permission

### Summary Protocol

When completing a task, AI agents must provide:

1. **Files Changed:** List of created/modified files
2. **What Was Done:** Brief summary of changes
3. **Testing Performed:** How it was verified
4. **Next Steps:** Any follow-up work needed
5. **Known Issues:** Any caveats or limitations

**Example:**
```
✅ Task Complete: Landing Page Implementation

Files Created:
- src/pages/LandingPage.tsx
- src/routes/landing.tsx
- src/routes/home.tsx

Files Modified:
- src/routes/index.tsx

What Was Done:
Created public landing page at `/` with hero section and CTAs.
Moved dashboard to `/home`. Updated auth flow.

Testing:
- Build passes: npm run build ✓
- Type check passes: npm run typecheck ✓
- Verified routes work correctly

Next Steps:
- Install framer-motion for animations (optional)
- Add bottom navigation component

Known Issues:
- None
```
