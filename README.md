# Atla - Philippine AI Travel Planner

An AI-powered travel planning application for exploring the Philippines. Built with React, FastAPI, and Google Gemini.

## Features

- **AI Chat Interface** - Plan your trip through natural conversation
- **Smart Itineraries** - AI-generated day-by-day travel plans
- **Interactive Maps** - Visualize your journey across Philippine destinations

## Tech Stack

- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS + TanStack Router
- **Backend:** FastAPI + Python 3.11 + SQLModel + asyncpg
- **Database:** PostgreSQL (Supabase)
- **AI:** Google Gemini + LangChain
- **Auth:** Supabase Auth

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

### 1. Clone & Setup

```bash
git clone <repo-url>
cd ph-travel-app
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` with your API keys (see [SETUP.md](SETUP.md) for details).

```bash
# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend/atla
npm install
cp .env.example .env
```

Edit `frontend/atla/.env` with your Supabase credentials.

```bash
npm run dev
```

### 4. Access the App

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup instructions with API keys
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - How to contribute
- **[docs/BRANCHING.md](docs/BRANCHING.md)** - Git workflow & branch naming
- **[docs/COMMITS.md](docs/COMMITS.md)** - Commit message conventions
- **[docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md)** - PR process
- **[AGENTS.md](AGENTS.md)** - AI agent guidelines & code style
- **[ARCH.md](ARCH.md)** - System architecture

## Development

### Backend Commands

```bash
cd backend
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head                               # Apply migrations
pytest                                             # Run tests
black app/                                         # Format code
ruff check app/                                    # Lint code
```

### Frontend Commands

```bash
cd frontend/atla
npm run dev         # Start dev server
npm run build       # Production build
npm run typecheck   # TypeScript check
npm run lint        # ESLint
```

## Contributing

We welcome contributions! Please read our [Contributing Guide](docs/CONTRIBUTING.md) to get started.

Quick summary:
- Branch from `main`: `git checkout -b feat/your-feature`
- Follow [Conventional Commits](docs/COMMITS.md)
- Create a Pull Request
- Ensure CI passes (build + type check)

