# 🇵🇭 Philippine AI Travel App - System Architecture

**Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Design Phase  
**ORM:** SQLModel

---

## Executive Summary

### Project Goal

Build a Philippine-focused AI travel planning web application that helps users discover destinations, generate personalized itineraries, and visualize trips through an intuitive chat-first interface powered by Google Gemini.

### Core Technology Choices

- **Frontend**: React + TypeScript + Vite + Tailwind + shadcn/ui
- **Backend**: FastAPI + Python 3.11+
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **AI**: LangChain + Google Gemini 2.5 flash-lite
- **Database**: Supabase (PostgreSQL)
- **Cache**: Upstash Redis
- **Search**: Brave Search API
- **Weather**: OpenWeather API
- **Destinations**: Tripadvisor API
- **Maps**: MapCN (MapLibre + OpenStreetMap)
- **Auth**: Supabase Auth (Email/Password + Username)

---

## Technology Stack

### Backend Stack

```json
{
  "framework": "FastAPI 0.109",
  "language": "Python 3.11+",
  "orm": "SQLModel 0.0.14",
  "database_driver": "asyncpg",
  "migrations": "Alembic",
  "ai_framework": "LangChain 0.1",
  "llm": "Google Gemini 2.5 flash-lite",
  "validation": "Pydantic v2 (built into SQLModel)",
  "auth": "Supabase Auth",
  "cache": "Redis (via Upstash)",
  "http_client": "httpx"
}
```

### Why SQLModel?

**SQLModel** = SQLAlchemy + Pydantic

**Benefits:**
1. **Single Source of Truth**: Same model for DB, API, and validation
2. **Type Safety**: Full typing support with mypy
3. **Pydantic Integration**: Automatic validation and serialization
4. **SQLAlchemy Power**: Full ORM capabilities with migrations
5. **FastAPI Native**: Created by FastAPI author (Sebastián Ramírez)

**Example:**
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Trip(SQLModel, table=True):
    __tablename__ = "trips"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id")
    title: str
    destination: str
    days: int = Field(ge=1, le=30)
    
    # This same model works for:
    # - Database operations
    # - API request/response
    # - Validation
    # - Type checking
```

### Backend Dependencies

```txt
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Database & ORM
sqlmodel==0.0.14
asyncpg==0.29.0
alembic==1.13.0

# AI
langchain==0.1.0
langchain-google-genai==0.0.6

# Auth & Services
supabase==2.3.0
redis==5.0.1
httpx==0.26.0

# Utilities
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic-settings==2.1.0
pydantic-to-typescript==1.0.10

# Development
pytest==7.4.0
pytest-asyncio==0.21.0
black==23.12.0
ruff==0.1.0
```

---

## Backend Architecture with SQLModel

### Directory Structure

```
backend/
├── alembic/                        # Database migrations
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── alembic.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app initialization
│   ├── config.py                   # Settings (Pydantic Settings)
│   │
│   ├── models/                     # SQLModel models
│   │   ├── __init__.py
│   │   ├── user.py                 # User & UserProfile models
│   │   ├── trip.py                 # Trip, TripDay, Activity models
│   │   ├── place.py                # Place model
│   │   ├── chat.py                 # ChatSession model
│   │   └── analytics.py            # Analytics models
│   │
│   ├── schemas/                    # Pydantic schemas (non-table)
│   │   ├── __init__.py
│   │   ├── travel.py               # TravelIntent, CostEstimate
│   │   ├── api.py                  # API request/response models
│   │   └── auth.py                 # Auth request/response
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                 # Dependency injection
│   │   ├── chat.py                 # POST /api/chat
│   │   ├── trips.py                # Trip CRUD endpoints
│   │   ├── places.py               # Place search/details
│   │   └── auth.py                 # Auth endpoints
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py              # Database session management
│   │   ├── engine.py               # SQLModel engine setup
│   │   └── init_db.py              # Database initialization
│   │
│   ├── repositories/               # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                 # Base repository
│   │   ├── trip_repo.py            # Trip repository
│   │   ├── place_repo.py           # Place repository
│   │   └── user_repo.py            # User repository
│   │
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   ├── chat_service.py         # Chat orchestration
│   │   ├── trip_service.py         # Trip operations
│   │   └── user_service.py         # User management
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── llm.py                  # Gemini client
│   │   │
│   │   ├── chains/
│   │   │   ├── __init__.py
│   │   │   ├── intent_extraction.py
│   │   │   ├── itinerary_generation.py
│   │   │   └── followup_handler.py
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search.py           # Brave Search
│   │   │   ├── scraper.py          # Web scraping
│   │   │   └── places_db.py        # Query places
│   │   │
│   │   └── prompts/
│   │       ├── intent_extraction.txt
│   │       └── itinerary_generation.txt
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── supabase_client.py      # Supabase auth
│   │   ├── jwt.py                  # JWT utilities
│   │   └── middleware.py           # Auth middleware
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── redis_client.py         # Redis client
│   │   └── strategies.py           # Cache strategies
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── cors.py
│   │   ├── rate_limit.py
│   │   ├── logging.py
│   │   └── error_handler.py
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── metrics.py
│   │   └── tracing.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/
│   ├── conftest.py
│   ├── test_models/
│   ├── test_api/
│   └── test_services/
│
├── scripts/
│   ├── seed_places.py
│   └── generate_types.py
│
├── .env.example
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── fly.toml
```

---

## SQLModel Models

### User Models

**File**: `app/models/user.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr

class UserProfile(SQLModel, table=True):
    """Extended user profile (auth.users managed by Supabase)"""
    __tablename__ = "user_profiles"
    
    id: str = Field(primary_key=True)  # Matches Supabase auth.users.id
    username: str = Field(unique=True, index=True, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr
    avatar_url: Optional[str] = None
    preferences: dict = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    trips: List["Trip"] = Relationship(back_populates="user")
    chat_sessions: List["ChatSession"] = Relationship(back_populates="user")
    saved_places: List["SavedPlace"] = Relationship(back_populates="user")

# Response model (without sensitive data)
class UserProfilePublic(SQLModel):
    id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

# Create/Update models
class UserProfileCreate(SQLModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None

class UserProfileUpdate(SQLModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
```

### Trip Models

**File**: `app/models/trip.py`

```python
from sqlmodel import SQLModel, Field, Relationship, Column
from typing import Optional, List, Literal
from datetime import datetime, date
from sqlalchemy import ARRAY, String

class Trip(SQLModel, table=True):
    __tablename__ = "trips"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    title: str = Field(max_length=200)
    summary: Optional[str] = None
    destination: str = Field(index=True, max_length=100)
    days: int = Field(ge=1, le=30)
    budget: Optional[Literal["low", "mid", "luxury"]] = "mid"
    travel_style: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String))
    )
    companions: Optional[Literal["solo", "couple", "friends", "family"]] = "solo"
    time_of_year: Optional[str] = Field(default=None, max_length=50)
    total_budget_min: Optional[int] = None
    total_budget_max: Optional[int] = None
    is_public: bool = Field(default=False)
    view_count: int = Field(default=0)
    created_from_template_id: Optional[int] = Field(default=None, foreign_key="trip_templates.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: UserProfile = Relationship(back_populates="trips")
    trip_days: List["TripDay"] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    analytics: List["TripAnalytics"] = Relationship(back_populates="trip")

class TripDay(SQLModel, table=True):
    __tablename__ = "trip_days"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trips.id", index=True)
    day_number: int = Field(ge=1)
    title: str = Field(max_length=200)
    date: Optional[date] = None
    total_cost_min: Optional[int] = None
    total_cost_max: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    trip: Trip = Relationship(back_populates="trip_days")
    activities: List["Activity"] = Relationship(
        back_populates="trip_day",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Activity(SQLModel, table=True):
    __tablename__ = "activities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_day_id: int = Field(foreign_key="trip_days.id", index=True)
    name: str = Field(max_length=200)
    description: Optional[str] = None
    category: Literal["attraction", "restaurant", "accommodation", "transport"]
    place_id: Optional[str] = Field(default=None, foreign_key="places.id", index=True)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    address: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    cost_min: Optional[int] = None
    cost_max: Optional[int] = None
    start_time: Optional[str] = None  # TIME stored as string "HH:MM"
    end_time: Optional[str] = None
    booking_required: bool = Field(default=False)
    booking_url: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    trip_day: TripDay = Relationship(back_populates="activities")
    place: Optional["Place"] = Relationship(back_populates="activities")

# Response models
class TripPublic(SQLModel):
    id: int
    title: str
    summary: Optional[str]
    destination: str
    days: int
    budget: Optional[str]
    created_at: datetime

class TripDetail(TripPublic):
    trip_days: List["TripDayDetail"]
    total_budget_min: Optional[int]
    total_budget_max: Optional[int]

class TripDayDetail(SQLModel):
    day_number: int
    title: str
    date: Optional[date]
    activities: List["ActivityDetail"]

class ActivityDetail(SQLModel):
    name: str
    description: Optional[str]
    category: str
    latitude: Optional[float]
    longitude: Optional[float]
    start_time: Optional[str]
    duration_minutes: Optional[int]
```

### Place Models

**File**: `app/models/place.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Place(SQLModel, table=True):
    __tablename__ = "places"
    
    id: str = Field(primary_key=True)  # External ID (e.g., Google Place ID)
    name: str = Field(index=True, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, index=True, max_length=50)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    price_level: Optional[int] = Field(default=None, ge=1, le=4)
    opening_hours: dict = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    photos: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "JSONB"})
    metadata: dict = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    source: Optional[str] = Field(default=None, max_length=50)  # 'brave_search', 'manual', etc.
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    activities: List["Activity"] = Relationship(back_populates="place")
    saved_by: List["SavedPlace"] = Relationship(back_populates="place")

class SavedPlace(SQLModel, table=True):
    __tablename__ = "saved_places"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    place_id: str = Field(foreign_key="places.id", index=True)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: UserProfile = Relationship(back_populates="saved_places")
    place: Place = Relationship(back_populates="saved_by")
```

### Chat Models

**File**: `app/models/chat.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    messages: List[dict] = Field(default_factory=list, sa_column_kwargs={"type_": "JSONB"})
    current_intent: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    trip_id: Optional[int] = Field(default=None, foreign_key="trips.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    user: UserProfile = Relationship(back_populates="chat_sessions")
```

### Analytics Models

**File**: `app/models/analytics.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class TripAnalytics(SQLModel, table=True):
    __tablename__ = "trip_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trips.id", index=True)
    user_id: Optional[str] = Field(default=None, foreign_key="user_profiles.id")
    event_type: str = Field(index=True, max_length=50)
    metadata: dict = Field(default_factory=dict, sa_column_kwargs={"type_": "JSONB"})
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    trip: Optional[Trip] = Relationship(back_populates="analytics")

class TripTemplate(SQLModel, table=True):
    __tablename__ = "trip_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    destination: str = Field(index=True, max_length=100)
    days: int = Field(ge=1, le=30)
    budget: Optional[str] = Field(default=None, max_length=20)
    travel_style: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "ARRAY(String)"})
    icon: Optional[str] = Field(default=None, max_length=10)
    template_data: dict = Field(sa_column_kwargs={"type_": "JSONB"})
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Database Session Management

### Engine Setup

**File**: `app/db/engine.py`

```python
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Async engine for SQLModel
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
```

### Session Dependency

**File**: `app/db/session.py`

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import async_session

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    
    Usage:
        @app.get("/trips")
        async def get_trips(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Database Initialization

**File**: `app/db/init_db.py`

```python
from sqlmodel import SQLModel
from app.db.engine import engine
from app.models import *  # Import all models

async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

async def drop_db():
    """Drop all tables (use with caution!)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

---

## Repository Pattern

### Base Repository

**File**: `app/repositories/base.py`

```python
from typing import TypeVar, Generic, Type, Optional, List
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get by ID"""
        result = await self.session.get(self.model, id)
        return result
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, obj: ModelType) -> ModelType:
        """Create new record"""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        """Update existing record"""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def delete(self, id: int) -> bool:
        """Delete record"""
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False
```

### Trip Repository

**File**: `app/repositories/trip_repo.py`

```python
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.trip import Trip, TripDay, Activity
from app.repositories.base import BaseRepository

class TripRepository(BaseRepository[Trip]):
    def __init__(self, session: AsyncSession):
        super().__init__(Trip, session)
    
    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Trip]:
        """Get all trips for a user"""
        result = await self.session.execute(
            select(Trip)
            .where(Trip.user_id == user_id)
            .order_by(Trip.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_with_days(self, trip_id: int, user_id: str) -> Optional[Trip]:
        """Get trip with all days and activities"""
        result = await self.session.execute(
            select(Trip)
            .where(Trip.id == trip_id, Trip.user_id == user_id)
            .options(
                selectinload(Trip.trip_days).selectinload(TripDay.activities)
            )
        )
        return result.scalar_one_or_none()
    
    async def increment_views(self, trip_id: int):
        """Increment view count"""
        trip = await self.get(trip_id)
        if trip:
            trip.view_count += 1
            await self.update(trip)
```

---

## API Endpoints with SQLModel

### Trip Endpoints

**File**: `app/api/trips.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_session
from app.models.trip import Trip, TripPublic, TripDetail
from app.models.user import UserProfile
from app.repositories.trip_repo import TripRepository
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/trips", tags=["trips"])

@router.get("/", response_model=List[TripPublic])
async def get_trips(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get all trips for authenticated user"""
    repo = TripRepository(session)
    trips = await repo.get_by_user(current_user.id, skip, limit)
    return trips

@router.get("/{trip_id}", response_model=TripDetail)
async def get_trip(
    trip_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get specific trip with full details"""
    repo = TripRepository(session)
    trip = await repo.get_with_days(trip_id, current_user.id)
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    return trip

@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete trip"""
    repo = TripRepository(session)
    
    # Verify ownership
    trip = await repo.get(trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    await repo.delete(trip_id)
    return {"success": True}
```

---

## Alembic Migrations

### Alembic Configuration

**File**: `alembic/env.py`

```python
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.config import settings
from app.models import *  # Import all models
from sqlmodel import SQLModel

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
```

### Initial Migration

**File**: `alembic/versions/001_initial_schema.py`

```python
"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-06
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # User profiles
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('preferences', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_user_profiles_username', 'user_profiles', ['username'])
    
    # Places
    op.create_table(
        'places',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('price_level', sa.Integer(), nullable=True),
        sa.Column('opening_hours', postgresql.JSONB(), nullable=False),
        sa.Column('photos', postgresql.JSONB(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Trips
    op.create_table(
        'trips',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('days', sa.Integer(), nullable=False),
        sa.Column('budget', sa.String(), nullable=True),
        sa.Column('travel_style', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('companions', sa.String(), nullable=True),
        sa.Column('time_of_year', sa.String(length=50), nullable=True),
        sa.Column('total_budget_min', sa.Integer(), nullable=True),
        sa.Column('total_budget_max', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('created_from_template_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trips_user_id', 'trips', ['user_id'])
    op.create_index('ix_trips_destination', 'trips', ['destination'])
    
    # Continue with other tables...

def downgrade() -> None:
    op.drop_table('trips')
    op.drop_table('places')
    op.drop_table('user_profiles')
```

---

## Configuration with Pydantic Settings

**File**: `app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str  # PostgreSQL async URL
    
    # Supabase (for Auth)
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # LLM
    GOOGLE_API_KEY: str
    
    # Search
    BRAVE_API_KEY: str
    
    # Cache
    REDIS_URL: str
    
    # Observability
    SENTRY_DSN: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "https://yourapp.vercel.app"
    ]

settings = Settings()
```

---

## Frontend Architecture

The frontend is built as a modern React application with a focus on performance and developer experience. See the detailed documentation in `frontend/atla/docs/`.

### Frontend Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 19 | UI library with concurrent features |
| **Build Tool** | Vite | Fast development and building |
| **Language** | TypeScript | Type safety across the app |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | shadcn/ui | Accessible UI components |
| **Routing** | TanStack Router | Type-safe file-based routing |
| **State (Server)** | TanStack Query | Server state management |
| **State (Client)** | Zustand | Client state management |
| **Animations** | Framer Motion | Smooth transitions |
| **Maps** | MapCN (MapLibre) | Philippine-focused maps |
| **Auth** | Supabase Auth | Authentication |
| **HTTP** | Axios | API requests |

### Frontend Documentation

- **[ARCHITECTURE.md](frontend/atla/docs/ARCHITECTURE.md)** - Overall architecture and file structure
- **[DATA_FLOW.md](frontend/atla/docs/DATA_FLOW.md)** - TanStack Query patterns and data fetching
- **[ROUTING.md](frontend/atla/docs/ROUTING.md)** - File-based routing with TanStack Router
- **[STATE_MANAGEMENT.md](frontend/atla/docs/STATE_MANAGEMENT.md)** - Zustand store patterns
- **[.env.example](frontend/atla/.env.example)** - Environment variables template

### Key Architectural Decisions

1. **File-Based Routing**: Routes are defined by file structure in `src/routes/`, providing automatic type safety and code splitting.

2. **Two-Layer State Management**:
   - **TanStack Query**: For server state (trips, places, user data) with caching
   - **Zustand**: For client state (auth, UI, temporary chat messages)

3. **No Waterfalls**: Trip details are fetched as nested data (trip + days + activities in one request) to prevent sequential API calls.

4. **Bottom Navigation**: Hide-on-scroll bottom tab bar for mobile-first design with Framer Motion animations.

5. **Chat-First Interface**: Natural language trip planning with AI, where conversations reset on refresh but saved trips persist.

### Frontend Directory Structure

```
frontend/atla/src/
├── routes/              # File-based routes (pages)
│   ├── __root.tsx      # Root layout
│   ├── index.tsx       # Chat page
│   ├── trips.index.tsx # Trips list
│   ├── trips.$tripId.tsx # Trip detail
│   ├── explore.index.tsx # Explore places
│   ├── profile.index.tsx # Profile
│   ├── login.tsx       # Login
│   └── signup.tsx      # Signup
├── components/         # React components
│   ├── ui/            # shadcn components
│   ├── layout/        # Layout components
│   ├── chat/          # Chat feature
│   ├── trips/         # Trip feature
│   └── places/        # Places feature
├── hooks/             # Custom React hooks
├── lib/               # Utilities & config
├── stores/            # Zustand stores
└── types/             # TypeScript types
```

### Getting Started

```bash
cd frontend/atla
npm install
cp .env.example .env
# Edit .env with your Supabase credentials
npm run dev
```

---

Now I'll create the complete project scaffolding with all the necessary files.
