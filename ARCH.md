# 🇵🇭 Atla Travel Planning App - System Architecture

**Version:** 1.1  
**Last Updated:** February 2026  
**Status:** MVP In Progress  
**ORM:** SQLModel

---

> 🎯 **This document describes the TARGET architecture and project vision.**
> 
> 📚 **For implementation details and current state, see:**
> - **[Backend Docs](backend/docs/)** - Database, patterns, architecture explained
> - **[Frontend Docs](frontend/atla/docs/)** - React architecture and patterns
> - **[AGENTS.md](AGENTS.md)** - Development guidelines and commands

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
├── alembic/                        # Database migrations ✅
│   ├── versions/                   # Migration files
│   ├── env.py                      # Async SQLModel config
│   └── alembic.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app initialization ✅
│   ├── config.py                   # Settings (Pydantic Settings) ✅
│   │
│   ├── models/                     # SQLModel models ✅
│   │   ├── __init__.py
│   │   ├── user.py                 # User & UserProfile models ✅
│   │   ├── trip.py                 # Trip, TripDay, Activity models ✅
│   │   ├── place.py                # Place, SavedPlace models ✅
│   │   ├── chat.py                 # ChatSession model ⏳ PLANNED
│   │   └── analytics.py            # Analytics models ⏳ PLANNED
│   │
│   ├── schemas/                    # Pydantic schemas (non-table) ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── travel.py               # TravelIntent, CostEstimate
│   │   ├── api.py                  # API request/response models
│   │   └── auth.py                 # Auth request/response
│   │
│   ├── api/                        # API endpoints ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── deps.py                 # Dependency injection
│   │   ├── chat.py                 # POST /api/chat
│   │   ├── trips.py                # Trip CRUD endpoints
│   │   ├── places.py               # Place search/details
│   │   └── auth.py                 # Auth endpoints
│   │
│   ├── db/                         # Database layer ✅
│   │   ├── __init__.py
│   │   ├── session.py              # Database session management ✅
│   │   ├── engine.py               # SQLModel engine setup ✅
│   │   └── init_db.py              # Database initialization ⏳ PLANNED
│   │
│   ├── repositories/               # Data access layer ✅
│   │   ├── __init__.py
│   │   ├── base.py                 # Base repository ✅
│   │   ├── trip_repo.py            # Trip repository ✅
│   │   ├── place_repo.py           # Place repository ✅
│   │   └── user_repo.py            # User repository ✅
│   │
│   ├── services/                   # Business logic ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── chat_service.py         # Chat orchestration
│   │   ├── trip_service.py         # Trip operations
│   │   └── user_service.py         # User management
│   │
│   ├── ai/                         # AI Layer ⏳ PLANNED
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
│   ├── auth/                       # Authentication ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── supabase_client.py      # Supabase auth
│   │   ├── jwt.py                  # JWT utilities
│   │   └── middleware.py           # Auth middleware
│   │
│   ├── cache/                      # Caching ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── redis_client.py         # Redis client
│   │   └── strategies.py           # Cache strategies
│   │
│   ├── middleware/                 # Middleware ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── cors.py                 # Already in main.py
│   │   ├── rate_limit.py
│   │   ├── logging.py
│   │   └── error_handler.py
│   │
│   ├── observability/              # Monitoring ⏳ PLANNED
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── metrics.py
│   │   └── tracing.py
│   │
│   └── utils/                      # Utilities ⏳ PLANNED
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/                          # Test suite ⏳ PLANNED
│   ├── conftest.py
│   ├── test_models/
│   ├── test_api/
│   └── test_services/
│
├── scripts/                        # Utility scripts ⏳ PLANNED
│   ├── seed_places.py
│   └── generate_types.py
│
├── docs/                           # Documentation ✅
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   └── PATTERNS.md
│
├── .env.example                    # Environment template ✅
├── requirements.txt                # Dependencies ✅
├── pyproject.toml                  # Tool config ✅
├── Dockerfile                      # Container ⏳ PLANNED
└── fly.toml                        # Deployment ⏳ PLANNED
```

**Legend:**
- ✅ **Implemented** - Code exists and working
- ⏳ **Planned** - Specified in architecture, not yet built

---

## SQLModel Models

### User Models

**File**: `app/models/user.py` ✅

```python
from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import JSONB

class UserProfile(SQLModel, table=True):
    """Extended user profile (auth.users managed by Supabase)"""
    __tablename__ = "user_profiles"
    
    id: str = Field(primary_key=True)  # Matches Supabase auth.users.id
    username: str = Field(unique=True, index=True, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr
    avatar_url: Optional[str] = None
    preferences: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

**File**: `app/models/trip.py` ✅

```python
from sqlmodel import SQLModel, Field, Column
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import JSONB

class Trip(SQLModel, table=True):
    """User trip itineraries"""
    __tablename__ = "trips"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    title: str = Field(max_length=200)
    summary: Optional[str] = None
    destination: str = Field(index=True, max_length=100)
    days: int = Field(ge=1, le=30)
    budget: Optional[str] = Field(default="mid", max_length=20)
    travel_style: List[str] = Field(default_factory=list, sa_column=Column(JSONB, default=list))
    companions: Optional[str] = Field(default="solo", max_length=20)
    time_of_year: Optional[str] = Field(default=None, max_length=50)
    total_budget_min: Optional[int] = None
    total_budget_max: Optional[int] = None
    is_public: bool = Field(default=False)
    view_count: int = Field(default=0)
    created_from_template_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TripDay(SQLModel, table=True):
    """Individual days within a trip"""
    __tablename__ = "trip_days"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trips.id", index=True)
    day_number: int = Field(ge=1)
    title: str = Field(max_length=200)
    trip_date: Optional[date] = None
    total_cost_min: Optional[int] = None
    total_cost_max: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Activity(SQLModel, table=True):
    """Activities within a trip day"""
    __tablename__ = "activities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_day_id: int = Field(foreign_key="trip_days.id", index=True)
    name: str = Field(max_length=200)
    description: Optional[str] = None
    category: str = Field(max_length=50)
    place_id: Optional[str] = Field(default=None, foreign_key="places.id", index=True)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    address: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    cost_min: Optional[int] = None
    cost_max: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    booking_required: bool = Field(default=False)
    booking_url: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    total_budget_min: Optional[int]
    total_budget_max: Optional[int]
    is_public: bool
    view_count: int
```

### Place Models

**File**: `app/models/place.py` ✅

```python
from sqlmodel import SQLModel, Field, Column
from typing import Optional, List
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class Place(SQLModel, table=True):
    """Destinations, restaurants, hotels, attractions"""
    __tablename__ = "places"
    
    id: str = Field(primary_key=True)  # External ID (Google Place ID, etc.)
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
    opening_hours: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    photos: List[str] = Field(default_factory=list, sa_column=Column(JSONB, default=list))
    place_metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    source: Optional[str] = Field(default=None, max_length=50)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SavedPlace(SQLModel, table=True):
    """Places saved by users"""
    __tablename__ = "saved_places"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    place_id: str = Field(foreign_key="places.id", index=True)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Response models
class PlacePublic(SQLModel):
    id: str
    name: str
    category: Optional[str]
    latitude: float
    longitude: float
    rating: Optional[float]

class PlaceDetail(PlacePublic):
    description: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    price_level: Optional[int]
    opening_hours: dict
    photos: List[str]
```

### Chat Models (Planned)

**File**: `app/models/chat.py` ⏳

```python
from sqlmodel import SQLModel, Field, Column
from typing import Optional, List
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class ChatSession(SQLModel, table=True):
    """Chat conversation storage"""
    __tablename__ = "chat_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.id", index=True)
    messages: List[dict] = Field(default_factory=list, sa_column=Column(JSONB, default=list))
    current_intent: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    trip_id: Optional[int] = Field(default=None, foreign_key="trips.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

### Analytics Models (Planned)

**File**: `app/models/analytics.py` ⏳

```python
from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class TripAnalytics(SQLModel, table=True):
    """Analytics tracking events"""
    __tablename__ = "trip_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trips.id", index=True)
    user_id: Optional[str] = Field(default=None, foreign_key="user_profiles.id")
    event_type: str = Field(index=True, max_length=50)
    event_metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB, default=dict))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class TripTemplate(SQLModel, table=True):
    """Pre-built trip templates"""
    __tablename__ = "trip_templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    destination: str = Field(index=True, max_length=100)
    days: int = Field(ge=1, le=30)
    budget: Optional[str] = Field(default=None, max_length=20)
    travel_style: List[str] = Field(default_factory=list, sa_column=Column(JSONB, default=list))
    icon: Optional[str] = Field(default=None, max_length=10)
    template_data: dict = Field(sa_column=Column(JSONB))
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Database Session Management

### Engine Setup

**File**: `app/db/engine.py` ✅

```python
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

**File**: `app/db/session.py` ✅

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

### Database Initialization (Planned)

**File**: `app/db/init_db.py` ⏳

```python
from sqlmodel import SQLModel
from app.db.engine import engine
from app.models import *  # Import all models

async def init_db():
    """Create all tables (for development only)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def drop_db():
    """Drop all tables (use with caution!)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

> 💡 **Note**: In production, use Alembic migrations instead of `init_db()`

---

## Repository Pattern

### Base Repository

**File**: `app/repositories/base.py` ✅

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

### Repository Implementations

**Implemented Repositories:** ✅
- `UserRepository` - User operations
- `PlaceRepository` - Place operations
- `SavedPlaceRepository` - Saved places operations
- `TripRepository` - Trip operations
- `TripDayRepository` - Trip day operations
- `ActivityRepository` - Activity operations

See [backend docs](backend/docs/PATTERNS.md) for implementation details.

---

## API Endpoints (Planned)

### Trip Endpoints

**File**: `app/api/trips.py` ⏳

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
```

---

## Alembic Migrations

### Configuration

**File**: `alembic/env.py` ✅

See current implementation in `backend/alembic/env.py`

### Creating Migrations

```bash
cd backend

# Create new migration
venv\Scripts\alembic.exe revision --autogenerate -m "Description"

# Apply migrations
venv\Scripts\alembic.exe upgrade head

# Rollback
venv\Scripts\alembic.exe downgrade -1
```

### Current Migrations

- `7807e5e16761` - Initial migration with user_profiles table
- `dd94b48b3f25` - Add places, trips, activities tables

---

## Configuration

**File**: `app/config.py` ✅

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    
    # Database (uses DEV_DATABASE_URL or PROD_DATABASE_URL based on ENVIRONMENT)
    DEV_DATABASE_URL: str
    PROD_DATABASE_URL: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # APIs
    GOOGLE_API_KEY: str
    BRAVE_API_KEY: str
    
    # Cache
    REDIS_URL: str
    
    # CORS (comma-separated string, parsed into list)
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    
    @property
    def DATABASE_URL(self) -> str:
        """Return appropriate database URL based on environment"""
        if self.ENVIRONMENT.lower() == "production":
            return self.PROD_DATABASE_URL
        return self.DEV_DATABASE_URL
    
    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
```

---

## Frontend Architecture

The frontend is built as a modern React application. See detailed documentation:

- **[Frontend Architecture](frontend/atla/docs/ARCHITECTURE.md)** - Overall structure
- **[Data Flow](frontend/atla/docs/DATA_FLOW.md)** - TanStack Query patterns
- **[Routing](frontend/atla/docs/ROUTING.md)** - File-based routing
- **[State Management](frontend/atla/docs/STATE_MANAGEMENT.md)** - Zustand patterns

### Frontend Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 19 | UI library |
| **Build Tool** | Vite | Development & building |
| **Language** | TypeScript | Type safety |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | shadcn/ui | UI components |
| **Routing** | TanStack Router | File-based routing |
| **State (Server)** | TanStack Query | Server state |
| **State (Client)** | Zustand | Client state |
| **Animations** | Framer Motion | Transitions |
| **Maps** | MapCN (MapLibre) | Philippine maps |
| **Auth** | Supabase Auth | Authentication |
| **HTTP** | Axios | API requests |

---

## Development Resources

### Documentation

- **[AGENTS.md](AGENTS.md)** - Development guidelines, commands, patterns
- **[backend/docs/](backend/docs/)** - Backend implementation details
  - [README.md](backend/docs/README.md) - Getting started
  - [ARCHITECTURE.md](backend/docs/ARCHITECTURE.md) - System design
  - [DATABASE.md](backend/docs/DATABASE.md) - Schema & models
  - [PATTERNS.md](backend/docs/PATTERNS.md) - Code patterns & examples
- **[frontend/atla/docs/](frontend/atla/docs/)** - Frontend documentation
- **[SETUP.md](SETUP.md)** - Environment setup guide

### Quick Commands

```bash
# Backend
cd backend
venv\Scripts\uvicorn.exe app.main:app --reload
venv\Scripts\alembic.exe upgrade head

# Frontend
cd frontend/atla
npm run dev
```

---

## Project Status Summary

### ✅ Implemented
- Database setup (PostgreSQL + asyncpg)
- SQLModel models (User, Trip, TripDay, Activity, Place, SavedPlace)
- Alembic migrations
- Repository pattern (Base, User, Place, Trip, Activity)
- Health check endpoint with DB verification
- Project documentation (ARCH.md, AGENTS.md, backend docs)

### ⏳ Planned / In Progress
- API endpoints (trips, places, auth)
- Services layer (business logic)
- Authentication (Supabase integration)
- AI integration (LangChain + Gemini)
- Frontend implementation
- Testing suite
- Deployment setup

---

*Last updated: February 2026*
