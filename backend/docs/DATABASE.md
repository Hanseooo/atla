# Database Guide

## Quick Start

```bash
# 1. Make sure you're in the backend directory with venv activated
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. Create a migration after changing models
alembic revision --autogenerate -m "Add new table"

# 3. Apply migrations to database
alembic upgrade head

# 4. Check status
alembic current
```

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

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserProfile(SQLModel, table=True):
    """User profile linked to Supabase Auth"""
    __tablename__ = "user_profiles"
    
    id: str = Field(primary_key=True)  # Supabase Auth ID
    username: Optional[str] = Field(unique=True, max_length=50)
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships:**
- One user has many trips
- One user has many saved places
- One user has many chat sessions

### 2. trips
**Purpose:** Store trip itineraries

**Analogy:** Like a travel binder with trip details

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

class Trip(SQLModel, table=True):
    """User trip itineraries"""
    __tablename__ = "trips"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    title: str = Field(max_length=200)
    destination: str = Field(index=True, max_length=100)
    days: int = Field(ge=1, le=30)
    budget: Optional[str] = Field(default="mid", max_length=20)
    travel_style: List[str] = Field(default_factory=list, sa_column=Column(JSONB, default=list))
    companions: Optional[str] = Field(default="solo", max_length=20)
    total_budget_min: Optional[int] = None
    total_budget_max: Optional[int] = None
    is_public: bool = Field(default=False)
    view_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships:**
- Belongs to one user
- Has many trip_days
- Can have many activities (through trip_days)

### 3. trip_days
**Purpose:** Break down trip into days

**Analogy:** Daily pages in a travel planner

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class TripDay(SQLModel, table=True):
    """Individual day in a trip"""
    __tablename__ = "trip_days"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trips.id", index=True)
    day_number: int
    title: Optional[str] = Field(default=None, max_length=200)
    date: Optional[date] = None
    total_cost_min: Optional[int] = None
    total_cost_max: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships:**
- Belongs to one trip
- Has many activities

### 4. activities
**Purpose:** Individual things to do

**Analogy:** Specific items on a daily schedule

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Activity(SQLModel, table=True):
    """Activities within a trip day"""
    __tablename__ = "activities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_day_id: int = Field(foreign_key="trip_days.id")
    name: str = Field(max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=50)
    place_id: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    duration_minutes: Optional[int] = None
    cost_min: Optional[int] = None
    cost_max: Optional[int] = None
    start_time: Optional[str] = Field(default=None, max_length=10)
    booking_required: bool = Field(default=False)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
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
alembic revision --autogenerate -m "Add places table"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history --verbose
```

### Troubleshooting

**"No module named 'alembic'"**
```bash
# Make sure you're in the backend directory and venv is activated
cd backend
venv\Scripts\activate  # Windows
alembic --version
```

**"Table already exists" error**
```bash
# If database was created manually, mark all migrations as applied
alembic stamp head
```

**"Can't locate revision" error**
```bash
# Reset to a known good state (WARNING: will delete unapplied migrations)
alembic downgrade base
alembic upgrade head
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
