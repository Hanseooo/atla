# Backend Documentation

Welcome to the Philippine Travel App backend! This documentation will help you understand how everything works.

## Quick Start

New here? Start with these:
1. **[Architecture Overview](ARCHITECTURE.md)** - Understand the big picture
2. **[Database Guide](DATABASE.md)** - Learn about our data models
3. **[Common Patterns](PATTERNS.md)** - How we organize code

## What's Inside

```
docs/
├── README.md           ← You are here!
├── ARCHITECTURE.md     ← How everything fits together
├── DATABASE.md         ← Data models explained
├── PATTERNS.md         ← Code patterns with examples
└── patterns/           ← Deep dives into specific patterns
    ├── models-vs-repositories.md
    └── async-explained.md
```

## Tech Stack (Quick Reference)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI | Web framework |
| **Database** | PostgreSQL + asyncpg | Data storage |
| **ORM** | SQLModel | Database models |
| **Migrations** | Alembic | Database version control |
| **AI** | LangChain + Gemini | Trip generation |
| **Auth** | Supabase | User authentication |

## Project Structure

```
backend/
├── app/                    ← Main application code
│   ├── models/            ← Data definitions (blueprints)
│   ├── repositories/      ← Database helpers
│   ├── db/               ← Database connection
│   ├── api/              ← API endpoints
│   ├── services/         ← Business logic
│   └── main.py           ← App entry point
├── alembic/              ← Database migrations
├── docs/                 ← This folder!
├── venv/                 ← Python packages
└── .env                  ← Secret settings
```

## Common Tasks

### Running the Server
```bash
cd backend
venv\Scripts\activate      # Windows
uvicorn app.main:app --reload
```

### Creating a Migration
```bash
cd backend
venv\Scripts\alembic.exe revision --autogenerate -m "Description"
venv\Scripts\alembic.exe upgrade head
```

### Adding a New Feature
1. Create/Update model in `app/models/`
2. Create repository in `app/repositories/` (if needed)
3. Create migration: `alembic revision --autogenerate`
4. Create API endpoint in `app/api/`

## Need Help?

- Check [PATTERNS.md](PATTERNS.md) for code examples
- Look at existing code in `app/models/` and `app/repositories/`
- Read the [Architecture Guide](ARCHITECTURE.md) for the big picture

---

**Next Step:** Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how everything works together!
