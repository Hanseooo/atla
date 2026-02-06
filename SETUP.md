# 🚀 Philippine Travel App - Setup Guide

Complete setup instructions for the Philippine AI Travel Planning application.

## Prerequisites

### Required Software

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/))

### Required Accounts & API Keys

1. **Supabase** (Free tier)
   - Sign up: https://supabase.com
   - Create a new project
   - Get: Project URL, Anon Key, Service Role Key

2. **Google Gemini API** (Free tier)
   - Sign up: https://makersuite.google.com/app/apikey
   - Create API key

3. **Brave Search API** (Free tier: 2,000 queries/month)
   - Sign up: https://brave.com/search/api/
   - Get API key

4. **Upstash Redis** (Free tier)
   - Sign up: https://upstash.com
   - Create Redis database
   - Get connection URL

---

## Project Setup

### 1. Clone the Project

```bash
cd your-projects-directory
# Extract the philippine-travel-app folder from the downloaded files
```

### 2. Backend Setup

```bash
cd philippine-travel-app/backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

#### Configure Backend Environment

Edit `backend/.env` with your credentials:

```bash
# Application
ENVIRONMENT=development
SECRET_KEY=your-random-secret-key-here-change-in-production

# Database (from Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Supabase Auth
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=eyJ[YOUR-ANON-KEY]
SUPABASE_SERVICE_ROLE_KEY=eyJ[YOUR-SERVICE-KEY]

# Google Gemini
GOOGLE_API_KEY=AIza[YOUR-API-KEY]

# Brave Search API
BRAVE_API_KEY=BSA[YOUR-API-KEY]

# Redis (from Upstash)
REDIS_URL=redis://default:[PASSWORD]@[ENDPOINT].upstash.io:6379

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Setup Database

**Option A: Using Alembic (Recommended)**

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Run migrations
alembic upgrade head
```

**Option B: Direct Table Creation**

In `backend/app/main.py`, uncomment:
```python
# await init_db()  # Uncomment this line
```

Then run:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
```

#### Configure Frontend Environment

Edit `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://[PROJECT-REF].supabase.co
VITE_SUPABASE_ANON_KEY=eyJ[YOUR-ANON-KEY]
```

---

## Running the Application

### Start Backend

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start FastAPI server
uvicorn app.main:app --reload
```

**Backend will be available at:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start Frontend

In a **new terminal**:

```bash
cd frontend

# Start Vite dev server
npm run dev
```

**Frontend will be available at:**
- App: http://localhost:5173

---

## Supabase Database Setup

### Create Tables via SQL Editor

Go to your Supabase project → SQL Editor → New Query, and run:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User profiles
CREATE TABLE public.user_profiles (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    email TEXT NOT NULL,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trips
CREATE TABLE public.trips (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    summary TEXT,
    destination TEXT NOT NULL,
    days INTEGER NOT NULL CHECK (days > 0 AND days <= 30),
    budget TEXT,
    travel_style TEXT[],
    companions TEXT,
    time_of_year TEXT,
    total_budget_min INTEGER,
    total_budget_max INTEGER,
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trip days
CREATE TABLE public.trip_days (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL CHECK (day_number > 0),
    title TEXT NOT NULL,
    date DATE,
    total_cost_min INTEGER,
    total_cost_max INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trip_id, day_number)
);

-- Activities
CREATE TABLE public.activities (
    id SERIAL PRIMARY KEY,
    trip_day_id INTEGER NOT NULL REFERENCES trip_days(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    place_id TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address TEXT,
    duration_minutes INTEGER,
    cost_min INTEGER,
    cost_max INTEGER,
    start_time TEXT,
    end_time TEXT,
    booking_required BOOLEAN DEFAULT FALSE,
    booking_url TEXT,
    notes TEXT,
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Places
CREATE TABLE public.places (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT,
    phone TEXT,
    website TEXT,
    rating DECIMAL(2, 1),
    price_level INTEGER,
    opening_hours JSONB DEFAULT '{}',
    photos JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    source TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat sessions
CREATE TABLE public.chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    messages JSONB NOT NULL DEFAULT '[]',
    current_intent JSONB,
    trip_id INTEGER REFERENCES trips(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Saved places
CREATE TABLE public.saved_places (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    place_id TEXT NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, place_id)
);

-- Create indexes
CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_destination ON trips(destination);
CREATE INDEX idx_trip_days_trip_id ON trip_days(trip_id);
CREATE INDEX idx_activities_trip_day_id ON activities(trip_day_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_saved_places_user_id ON saved_places(user_id);
```

### Enable Row Level Security (RLS)

```sql
-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE trip_days ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_places ENABLE ROW LEVEL SECURITY;

-- Policies for user_profiles
CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid()::text = id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid()::text = id);

-- Policies for trips
CREATE POLICY "Users can view own trips"
    ON trips FOR SELECT
    USING (auth.uid()::text = user_id OR is_public = TRUE);

CREATE POLICY "Users can insert own trips"
    ON trips FOR INSERT
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own trips"
    ON trips FOR UPDATE
    USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own trips"
    ON trips FOR DELETE
    USING (auth.uid()::text = user_id);

-- Policies for trip_days (follow trip ownership)
CREATE POLICY "Users can view trip days"
    ON trip_days FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM trips
            WHERE trips.id = trip_days.trip_id
            AND (trips.user_id = auth.uid()::text OR trips.is_public = TRUE)
        )
    );

CREATE POLICY "Users can modify own trip days"
    ON trip_days FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM trips
            WHERE trips.id = trip_days.trip_id
            AND trips.user_id = auth.uid()::text
        )
    );

-- Places are public (read-only for authenticated users)
CREATE POLICY "Places are publicly readable"
    ON places FOR SELECT
    TO authenticated
    USING (TRUE);

-- Chat sessions policies
CREATE POLICY "Users can view own chat sessions"
    ON chat_sessions FOR SELECT
    USING (auth.uid()::text = user_id);

CREATE POLICY "Users can manage own chat sessions"
    ON chat_sessions FOR ALL
    USING (auth.uid()::text = user_id);

-- Saved places policies
CREATE POLICY "Users can manage own saved places"
    ON saved_places FOR ALL
    USING (auth.uid()::text = user_id);
```

---

## Verification

### Test Backend

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","environment":"development"}
```

### Test Frontend

1. Open http://localhost:5173
2. You should see the homepage with "Philippine Travel Planner" title

---

## Development Workflow

### Backend Development

```bash
# Format code
black app/

# Lint
ruff app/

# Run tests
pytest

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

```bash
# Lint
npm run lint

# Format
npm run format

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'app'`
**Solution:** Make sure you're in the `backend/` directory and virtual environment is activated

**Problem:** Database connection errors
**Solution:** Check your `DATABASE_URL` format in `.env`. It should be:
```
postgresql+asyncpg://user:password@host:port/database
```

**Problem:** Import errors with SQLModel
**Solution:** Make sure all `__init__.py` files exist in model directories

### Frontend Issues

**Problem:** `Cannot find module '@/...'`
**Solution:** Check that `tsconfig.json` has the correct path alias configuration

**Problem:** CORS errors
**Solution:** Verify `ALLOWED_ORIGINS` in backend `.env` includes `http://localhost:5173`

**Problem:** Environment variables not loading
**Solution:** Make sure `.env` file exists and variables start with `VITE_`

---

## Next Steps

1. **Implement SQLModel Models**
   - Create models in `backend/app/models/`
   - Follow the ARCH.md for complete model definitions

2. **Implement LangChain Chains**
   - Intent extraction chain
   - Itinerary generation chain

3. **Build Frontend Components**
   - Chat interface
   - Clarification forms
   - Itinerary display
   - Map integration

4. **Add Authentication**
   - Implement Supabase auth flows
   - Protect API routes

5. **Deploy**
   - Frontend to Vercel
   - Backend to Fly.io

---

## Resources

- **Architecture Documentation**: `ARCH.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **React Query**: https://tanstack.com/query/latest
- **Supabase**: https://supabase.com/docs
- **LangChain**: https://python.langchain.com/docs/get_started/introduction

---

## Support

For questions or issues:
1. Check the ARCH.md for design decisions
2. Review API documentation at http://localhost:8000/docs
3. Check environment variable configuration

Happy coding! 🚀
