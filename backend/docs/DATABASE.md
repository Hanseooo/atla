# Database Guide

## Overview

We use **PostgreSQL** with **asyncpg** for async database operations, and **SQLModel** as our ORM.

**Why these choices?**
- PostgreSQL: Powerful, reliable, supports JSON
- asyncpg: Fast async driver for Python
- SQLModel: Combines SQLAlchemy + Pydantic (validation + ORM in one!)

## Current Schema

### Entity Relationship Diagram

```
┌──────────────────┐         ┌──────────────────┐
│   user_profiles  │         │      trips       │
├──────────────────┤         ├──────────────────┤
│ PK id            │◄────────│ FK user_id       │
│    username      │    1:M  │ PK id            │
│    email         │         │    title         │
│    display_name  │         │    destination   │
│    avatar_url    │         │    days          │
│    preferences   │         │    budget        │
│    created_at    │         │    created_at    │
│    updated_at    │         │    updated_at    │
└──────────────────┘         └────────┬─────────┘
                                      │
                                      │ 1:M
                                      ▼
                            ┌──────────────────┐
                            │    trip_days     │
                            ├──────────────────┤
                            │ PK id            │
                            │ FK trip_id       │
                            │    day_number    │
                            │    title         │
                            │    date          │
                            │    created_at    │
                            └────────┬─────────┘
                                     │
                                     │ 1:M
                                     ▼
                           ┌──────────────────┐
                           │    activities    │
                           ├──────────────────┤
                           │ PK id            │
                           │ FK trip_day_id   │
                           │    name          │
                           │    description   │
                           │    category      │
                           │    latitude      │
                           │    longitude     │
                           │    start_time    │
                           │    duration      │
                           │    created_at    │
                           └──────────────────┘

Legend:
  PK = Primary Key
  FK = Foreign Key
  1:M = One-to-Many relationship
```

## Tables Explained

### 1. user_profiles
**Purpose:** Store extended user information

**Analogy:** Like an employee ID card with extra details

```sql
CREATE TABLE user_profiles (
    id TEXT PRIMARY KEY,              -- Supabase Auth ID
    username TEXT UNIQUE,             -- @username
    email TEXT,                       -- user@example.com
    display_name TEXT,                -- "John Doe"
    avatar_url TEXT,                  -- Profile picture URL
    preferences JSONB,                -- {"theme": "dark", "currency": "PHP"}
    created_at TIMESTAMP,             -- When account created
    updated_at TIMESTAMP              -- When last updated
);
```

**Relationships:**
- One user has many trips
- One user has many saved places
- One user has many chat sessions

### 2. trips
**Purpose:** Store trip itineraries

**Analogy:** Like a travel binder with trip details

```sql
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,            -- Auto-increment ID
    user_id TEXT REFERENCES user_profiles(id),
    title TEXT,                       -- "Philippines Beach Trip"
    destination TEXT,                 -- "Cebu, Philippines"
    days INTEGER,                     -- Number of days (1-30)
    budget TEXT,                      -- "low", "mid", or "luxury"
    travel_style TEXT[],              -- ["adventure", "relaxation"]
    companions TEXT,                  -- "solo", "couple", "family"
    time_of_year TEXT,                -- "December 2024"
    total_budget_min INTEGER,         -- Estimated min cost
    total_budget_max INTEGER,         -- Estimated max cost
    is_public BOOLEAN,                -- Can others see this?
    view_count INTEGER,               -- How many views
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Relationships:**
- Belongs to one user
- Has many trip_days
- Can have many activities (through trip_days)

### 3. trip_days
**Purpose:** Break down trip into days

**Analogy:** Daily pages in a travel planner

```sql
CREATE TABLE trip_days (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id) ON DELETE CASCADE,
    day_number INTEGER,               -- Day 1, Day 2, etc.
    title TEXT,                       -- "Arrival in Cebu"
    date DATE,                        -- 2024-12-01
    total_cost_min INTEGER,           -- Estimated cost for day
    total_cost_max INTEGER,
    created_at TIMESTAMP
);
```

**Relationships:**
- Belongs to one trip
- Has many activities

### 4. activities
**Purpose:** Individual things to do

**Analogy:** Specific items on a daily schedule

```sql
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    trip_day_id INTEGER REFERENCES trip_days(id) ON DELETE CASCADE,
    name TEXT,                        -- "Visit Kawasan Falls"
    description TEXT,                 -- Details about the activity
    category TEXT,                    -- "attraction", "restaurant", "transport"
    place_id TEXT,                    -- Link to places table
    latitude DECIMAL(10,8),          -- GPS coordinates
    longitude DECIMAL(11,8),
    address TEXT,                     -- Full address
    duration_minutes INTEGER,         -- How long it takes
    cost_min INTEGER,                 -- Min cost
    cost_max INTEGER,                 -- Max cost
    start_time TEXT,                  -- "09:00"
    end_time TEXT,                    -- "12:00"
    booking_required BOOLEAN,         -- Need reservation?
    booking_url TEXT,                 -- Where to book
    notes TEXT,                       -- Additional notes
    sort_order INTEGER,               -- Display order
    created_at TIMESTAMP
);
```

**Relationships:**
- Belongs to one trip_day
- Can link to one place (optional)

## JSONB Fields

Some fields store flexible data as JSON:

### user_profiles.preferences
```json
{
    "theme": "dark",
    "currency": "PHP",
    "language": "en",
    "notifications": {
        "email": true,
        "push": false
    }
}
```

**Why JSONB?**
- ✅ Flexible schema (can add fields without migration)
- ✅ PostgreSQL can index and query JSON
- ✅ Perfect for user preferences that change often

## Migrations

### What Are Migrations?

**Analogy:** Like version control (git) but for your database schema

**Why use them?**
- Track schema changes over time
- Easy to deploy changes to production
- Can roll back if something breaks
- Team members can sync their databases

### How They Work

```
Development:                    Production:
┌──────────────┐              ┌──────────────┐
│   Database   │              │   Database   │
│    v1.0      │              │    v1.0      │
└──────┬───────┘              └──────┬───────┘
       │                             │
       ▼                             ▼
  Add new table                   Run migration
       │                             │
       ▼                             ▼
┌──────────────┐              ┌──────────────┐
│   Database   │              │   Database   │
│    v1.1      │              │    v1.1      │
└──────────────┘              └──────────────┘
```

### Common Commands

```bash
# Create a new migration (auto-detects changes)
cd backend
venv\Scripts\alembic.exe revision --autogenerate -m "Add places table"

# Apply all pending migrations
venv\Scripts\alembic.exe upgrade head

# Roll back one migration
venv\Scripts\alembic.exe downgrade -1

# Check current version
venv\Scripts\alembic.exe current
```

## Working with Data

### Creating Records

```python
from app.models.user import UserProfile
from app.repositories.user_repo import UserRepository
from app.db.session import get_session

# Using Repository (Recommended)
async def create_user_example():
    async with get_session() as session:
        repo = UserRepository(session)
        
        new_user = UserProfile(
            id="auth-user-id-123",
            username="john_doe",
            email="john@example.com",
            display_name="John Doe"
        )
        
        user = await repo.create(new_user)
        print(f"Created user: {user.username}")
```

### Querying Data

```python
# Get by ID
user = await repo.get(user_id)

# Get by email
user = await repo.get_by_email("john@example.com")

# Check if username exists
exists = await repo.username_exists("john_doe")

# Get multiple with pagination
users = await repo.get_multi(skip=0, limit=10)
```

### Relationships Example

```python
# Get user with their trips
async def get_user_with_trips(user_id: str):
    async with get_session() as session:
        # Get user
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(user_id)
        
        # Get user's trips (will need trip repository)
        trip_repo = TripRepository(session)
        trips = await trip_repo.get_by_user(user_id)
        
        return user, trips
```

## Best Practices

### 1. Always Use Repositories
❌ **Don't do this:**
```python
# Direct database access in API
@app.post("/users")
async def create_user(data):
    async with get_session() as session:
        session.add(UserProfile(**data))
        await session.commit()
```

✅ **Do this:**
```python
# Use repository
@app.post("/users")
async def create_user(data, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    user = await repo.create(UserProfile(**data))
    return user
```

### 2. Handle Relationships Carefully
```python
# When deleting a trip, cascade deletes its days and activities
# This is set up in the model with: cascade="all, delete-orphan"
```

### 3. Use Transactions
```python
# Multiple operations as one transaction
async def transfer_trip_ownership(trip_id, new_user_id):
    async with get_session() as session:
        trip = await trip_repo.get(trip_id)
        trip.user_id = new_user_id
        
        # Log the transfer
        log = TransferLog(trip_id=trip_id, new_owner=new_user_id)
        
        # Both saved together or both fail
        await session.add(trip)
        await session.add(log)
        await session.commit()
```

## Next Steps

1. Read [PATTERNS.md](PATTERNS.md) to learn common code patterns
2. Look at `app/models/user.py` for a real example
3. Check `app/repositories/user_repo.py` for repository patterns

---

**Questions?** Check the [Patterns Guide](PATTERNS.md) for detailed examples!
