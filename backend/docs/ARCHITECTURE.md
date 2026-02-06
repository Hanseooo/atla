# Architecture Overview

## The Big Picture

Think of our backend like a restaurant:

```
┌─────────────────────────────────────────────────────────────┐
│                     PHILIPPINE TRAVEL API                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CLIENT (Browser/App)                                       │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐                                            │
│  │   API Layer │  ← Waiters (FastAPI routes)                │
│  │   (app/api) │     Take orders, serve responses           │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │  Services   │  ← Chefs (Business logic)                  │
│  │(app/services)│    Process orders, make decisions          │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │Repositories │  ← Pantry staff (Database access)          │
│  │(app/repositories)│ Get ingredients from storage          │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │   Models    │  ← Recipe cards (Data definitions)         │
│  │  (app/models)│   Define what data looks like              │
│  └──────┬──────┘                                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │  Database   │  ← Storage room (PostgreSQL)               │
│  │(PostgreSQL) │    Where everything is stored              │
│  └─────────────┘                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Example

**Scenario:** User creates a new trip

```
┌─────────┐     ┌──────────────┐     ┌───────────┐     ┌─────────────┐     ┌──────────┐
│  Client │────▶│  API Route   │────▶│  Service  │────▶│ Repository │────▶│ Database │
│ (React) │     │ POST /trips  │     │TripService│     │TripRepository│     │PostgreSQL│
└─────────┘     └──────────────┘     └───────────┘     └─────────────┘     └──────────┘
     │                │                   │                  │                  │
     │ "Create trip"  │ Validate input    │ Business logic   │ "Save this"      │ Store data
     │                │ Call service      │ Call repository  │ Execute SQL      │ Return ID
     │                │                   │                  │                  │
     │◄───────────────│◄──────────────────│◄─────────────────│◄─────────────────│
     │ "Trip created!"│ Return response   │ Return result    │ Return saved obj │
```

## Layer Responsibilities

### 1. Models (`app/models/`)
**Analogy:** Recipe cards that define ingredients

**What they do:**
- Define data structure (what fields exist)
- Validate data types (email must be valid)
- Map to database tables

**Example:**
```python
class Trip(SQLModel, table=True):
    id: int
    title: str           # Must be a string
    days: int            # Must be a number
    destination: str     # Where they're going
```

### 2. Repositories (`app/repositories/`)
**Analogy:** Pantry staff who get/store ingredients

**What they do:**
- Talk to the database
- Save, update, delete, query data
- Keep database code in one place

**Example:**
```python
class TripRepository:
    async def get_by_user(user_id):
        # Go to database, find trips for this user
        return await session.execute(...)
```

### 3. Services (`app/services/`)
**Analogy:** Chefs who prepare the meal

**What they do:**
- Business logic (rules, calculations)
- Coordinate multiple repositories
- Call external APIs (AI, weather, etc.)

**Example:**
```python
class TripService:
    async def create_trip(data):
        # Validate budget
        # Calculate dates
        # Call AI to generate itinerary
        # Save via repository
```

### 4. API Layer (`app/api/`)
**Analogy:** Waiters who take orders

**What they do:**
- Receive HTTP requests
- Validate input
- Call services
- Return HTTP responses

**Example:**
```python
@app.post("/api/trips")
async def create_trip(data):
    # Validate request
    trip = await trip_service.create(data)
    return {"trip": trip}
```

## Key Patterns

### Dependency Injection
**Concept:** FastAPI automatically provides what functions need

**Example:**
```python
@app.get("/trips")
async def get_trips(
    session: AsyncSession = Depends(get_session),  # Auto-provided!
    current_user: User = Depends(get_current_user) # Auto-provided!
):
    # Don't need to create session or get user manually
    # FastAPI does it for us
```

**Analogy:** Like a restaurant where:
- Waiter brings order ticket (request)
- Kitchen automatically provides ingredients (session)
- Manager verifies customer ID (current_user)

### Async/Await
**Concept:** Handle many requests at once

**Visual:**
```
Without Async (Synchronous):
Request 1 ────────────────▶ Response 1
Request 2           ────────────────▶ Response 2
Request 3                   ────────────────▶ Response 3
                    (Each waits for previous)

With Async (Asynchronous):
Request 1 ────┐
Request 2 ────┼──▶ Process all at once
Request 3 ────┘
Response 1 ◀──┐
Response 2 ◀──┼──▶ Return when ready
Response 3 ◀──┘
```

## Database Connection Flow

```
┌────────────────────────────────────────────────────────────┐
│                    DATABASE CONNECTION                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Client makes request                                   │
│            │                                                │
│            ▼                                                │
│  2. FastAPI calls get_session()                            │
│            │                                                │
│            ▼                                                │
│  3. Creates AsyncSession from engine                       │
│            │                                                │
│            ▼                                                │
│  4. Repository uses session to query                       │
│            │                                                │
│            ▼                                                │
│  5. asyncpg talks to PostgreSQL                            │
│            │                                                │
│            ▼                                                │
│  6. Response returns, session closes                       │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## Project Dependencies

```
                    ┌──────────────────┐
                    │   FastAPI App    │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │  SQLModel │    │  Supabase │    │  LangChain│
    │  (Models) │    │   (Auth)  │    │    (AI)   │
    └─────┬─────┘    └───────────┘    └───────────┘
          │
          ▼
    ┌───────────┐
    │  asyncpg  │
    │(Database) │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │PostgreSQL │
    └───────────┘
```

## Next Steps

1. Read [DATABASE.md](DATABASE.md) to understand our data models
2. Read [PATTERNS.md](PATTERNS.md) for common code patterns
3. Look at existing code in `app/models/` and `app/repositories/`

---

**Questions?** Check the [Patterns Guide](PATTERNS.md) for detailed examples!
