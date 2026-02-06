# Common Patterns & Examples

This guide shows you how to write code the "Philippine Travel App way" with real examples and analogies.

## Table of Contents

1. [Models vs Repositories](#models-vs-repositories)
2. [The Async Pattern](#the-async-pattern)
3. [Dependency Injection](#dependency-injection)
4. [Creating a New Model](#creating-a-new-model)
5. [Creating a New Repository](#creating-a-new-repository)
6. [Common CRUD Operations](#common-crud-operations)

---

## Models vs Repositories

### The Analogy

**Think of a library:**

- **Models** = Book cards (define what a book is)
- **Repositories** = Librarians (find, add, remove books)
- **Database** = The actual bookshelves

### Visual Comparison

```
┌─────────────────────────────────────────────────────────────┐
│                      LIBRARY SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────┐                                          │
│  │    Model      │  "A book has: title, author, ISBN"       │
│  │  (Definition) │                                          │
│  └───────┬───────┘                                          │
│          │                                                   │
│          │ "Find me a book"                                  │
│          ▼                                                   │
│  ┌───────────────┐                                          │
│  │  Repository   │  Goes to shelves, finds book              │
│  │   (Actions)   │                                          │
│  └───────┬───────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌───────────────┐                                          │
│  │   Database    │  Actual books on shelves                  │
│  │   (Storage)   │                                          │
│  └───────────────┘                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Real Example

#### Model (The Definition)
```python
# app/models/book.py
from sqlmodel import SQLModel, Field
from typing import Optional

class Book(SQLModel, table=True):
    """Defines what a book looks like in our database"""
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    author: str = Field(max_length=100)
    isbn: str = Field(unique=True)
    published_year: Optional[int] = None
    
    # This tells the database:
    # - Create a table called "books"
    # - It has these columns
    # - ISBN must be unique
```

#### Repository (The Actions)
```python
# app/repositories/book_repo.py
from typing import Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.repositories.base import BaseRepository

class BookRepository(BaseRepository[Book]):
    """Handles all database operations for books"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Book, session)
    
    async def find_by_isbn(self, isbn: str) -> Optional[Book]:
        """Find a book by its ISBN number"""
        result = await self.session.execute(
            select(Book).where(Book.isbn == isbn)
        )
        return result.scalar_one_or_none()
    
    async def find_by_author(self, author: str) -> List[Book]:
        """Find all books by an author"""
        result = await self.session.execute(
            select(Book).where(Book.author == author)
        )
        return result.scalars().all()
    
    async def search_by_title(self, search_term: str) -> List[Book]:
        """Search books by title (partial match)"""
        result = await self.session.execute(
            select(Book).where(Book.title.contains(search_term))
        )
        return result.scalars().all()
```

#### Why Separate Them?

❌ **Without Separation (Messy)**
```python
# Everything in one place - hard to test and maintain
async def create_book(data):
    # Validate data (model job)
    # Connect to database (repo job)
    # Insert into database (repo job)
    # Return result (service job)
```

✅ **With Separation (Clean)**
```python
# Model: Just defines structure
class Book(SQLModel, table=True):
    title: str
    author: str

# Repository: Just handles database
class BookRepository(BaseRepository[Book]):
    async def find_by_author(self, author):
        return await self.session.execute(...)

# Service: Business logic
class BookService:
    async def create_book(self, data):
        book = Book(**data)
        return await self.repo.create(book)

# API: Just handles HTTP
@app.post("/books")
async def create_book_endpoint(data):
    return await book_service.create_book(data)
```

**Benefits:**
- ✅ Easy to test each part separately
- ✅ Can change database without touching API
- ✅ Code is reusable
- ✅ Clear responsibilities

---

## The Async Pattern

### Why Async?

**Analogy: Restaurant Waiter**

**Synchronous (Normal) Waiter:**
```
Customer 1: Order ─────▶ Wait ─────▶ Food ─────▶ Customer 1 done
                                    
Customer 2:           Order ─────▶ Wait ─────▶ Food ─────▶ Customer 2 done

Customer 3:                     Order ─────▶ Wait ─────▶ Food ─────▶ Customer 3 done

Time: ████████████████████████████████████████████████████████████████████
      (Serves one at a time - slow!)
```

**Asynchronous (Smart) Waiter:**
```
Customer 1: Order ──┐
Customer 2: Order ──┼──▶ Process all orders at once
Customer 3: Order ──┘

Customer 1: ◀── Food ──┐
Customer 2: ◀── Food ──┼──▶ Serve when ready
Customer 3: ◀── Food ──┘

Time: ████████████████████
      (Serves many at once - fast!)
```

### The `async` and `await` Keywords

```python
# Without async (synchronous) - blocks everything
import requests  # Regular library

def get_weather(city):
    response = requests.get(f"https://api.weather.com/{city}")  # WAIT HERE
    return response.json()  # Only runs after request completes

# With async (asynchronous) - doesn't block
import httpx  # Async library

async def get_weather(city):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")  # PAUSE
        return response.json()  # Resume when done
```

**Key Points:**
- `async def` = This function can pause
- `await` = Pause here, do other things while waiting
- While paused, the server can handle other requests!

### Real Example in Our Code

```python
# app/api/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.repositories.user_repo import UserRepository

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    """
    When a request comes in:
    1. FastAPI calls this function
    2. We need a database session - await get_session()
    3. We query the database - await repo.get_by_id()
    4. While waiting for DB, other requests can be processed!
    5. Return the user
    """
    repo = UserRepository(session)
    
    # PAUSE: Let other requests run while we wait for database
    user = await repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
```

### Visual Flow

```
Request 1 comes in ──▶ Create session ──▶ Query DB (PAUSE)
                                               │
Request 2 comes in ──▶ Create session ──▶ Query DB (PAUSE)
                                               │
Request 3 comes in ──▶ Create session ──▶ Query DB (PAUSE)
                                               │
DB responds to #1 ◀── Return result ◀──────────┘
DB responds to #2 ◀── Return result ◀──────────┘
DB responds to #3 ◀── Return result ◀──────────┘
```

### Common Async Mistakes

❌ **Forgot await**
```python
# WRONG: Returns a "coroutine" object, not the actual result
user = repo.get_by_id(user_id)  # Missing await!
```

✅ **Correct**
```python
# RIGHT: Actually waits for and returns the result
user = await repo.get_by_id(user_id)
```

❌ **Calling async function from sync**
```python
# WRONG: Can't await in a regular function
def regular_function():
    user = await repo.get_by_id(user_id)  # Error!
```

✅ **Correct**
```python
# RIGHT: Must use async def
async def async_function():
    user = await repo.get_by_id(user_id)  # Works!
```

---

## Dependency Injection

### What is it?

**Analogy: Restaurant Kitchen**

Without DI:
```python
# Chef has to go get ingredients themselves
def make_pasta():
    pot = get_pot()           # Go to storage
    pasta = get_pasta()       # Go to pantry
    water = get_water()       # Go to sink
    # Now finally cook
```

With DI:
```python
# Ingredients are brought to the chef
def make_pasta(pot, pasta, water):  # Provided automatically!
    # Just cook
```

### How FastAPI Does It

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.repositories.user_repo import UserRepository

# This function "provides" a database session
async def get_session():
    async with async_session() as session:
        yield session

# FastAPI automatically calls get_session() and provides it
@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)  # Auto-provided!
):
    # Don't need to create session manually
    # FastAPI did it for us
    repo = UserRepository(session)
    return await repo.get_by_id(user_id)
```

### Benefits

**Without DI:**
```python
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Have to create session manually every time
    async with async_session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)
        return user
    # Don't forget to close session!
```

**With DI:**
```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)  # Auto-managed!
):
    repo = UserRepository(session)
    return await repo.get_by_id(user_id)
    # Session automatically closed!
```

**Benefits:**
- ✅ Less boilerplate code
- ✅ Automatic cleanup (sessions close properly)
- ✅ Easy to test (can inject mock sessions)
- ✅ Can chain dependencies

### Chaining Dependencies

```python
# Dependency 1: Get database session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Dependency 2: Get current user (uses session)
async def get_current_user(
    token: str = Header(...),
    session: AsyncSession = Depends(get_session)
) -> UserProfile:
    # Verify token, get user from DB
    return user

# Dependency 3: Get user's trips (uses current user)
async def get_user_trips(
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[Trip]:
    repo = TripRepository(session)
    return await repo.get_by_user(current_user.id)

# API endpoint uses all dependencies
@app.get("/my-trips")
async def list_my_trips(
    trips: List[Trip] = Depends(get_user_trips)  # Gets trips automatically!
):
    return {"trips": trips}
```

---

## Creating a New Model

### Step-by-Step Guide

**Scenario:** We want to add a "Review" model for trip reviews

**Step 1:** Create the model file

```python
# app/models/review.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Review(SQLModel, table=True):
    """User reviews for trips"""
    __tablename__ = "reviews"
    
    # Primary key - auto-incrementing ID
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign keys - link to other tables
    trip_id: int = Field(foreign_key="trips.id")
    user_id: str = Field(foreign_key="user_profiles.id")
    
    # Review data
    rating: int = Field(ge=1, le=5)  # Must be 1-5
    comment: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships (for easy access)
    # trip: "Trip" = Relationship(back_populates="reviews")
    # user: "UserProfile" = Relationship(back_populates="reviews")
```

**Step 2:** Export it from models package

```python
# app/models/__init__.py

# ... existing imports ...
from app.models.review import Review

__all__ = [
    # ... existing exports ...
    "Review",
]
```

**Step 3:** Create migration

```bash
cd backend
venv\Scripts\alembic.exe revision --autogenerate -m "Add reviews table"
venv\Scripts\alembic.exe upgrade head
```

### Field Types Cheat Sheet

```python
from sqlmodel import Field
from typing import Optional
from datetime import datetime

# Basic types
id: int = Field(primary_key=True)                    # Integer PK
name: str                                           # String
age: Optional[int] = None                           # Nullable integer
is_active: bool = Field(default=True)              # Boolean with default

# Constraints
email: str = Field(unique=True)                     # Must be unique
username: str = Field(index=True)                   # Create index for fast lookup
price: float = Field(ge=0)                          # Must be >= 0
rating: int = Field(ge=1, le=5)                     # Must be 1-5

# Length constraints
title: str = Field(max_length=200)                  # Max 200 chars
description: str = Field(max_length=1000)

# Defaults
created_at: datetime = Field(default_factory=datetime.utcnow)
views: int = Field(default=0)

# JSON (flexible data)
metadata: dict = Field(default_factory=dict)

# Foreign keys
user_id: str = Field(foreign_key="user_profiles.id")
trip_id: int = Field(foreign_key="trips.id")
```

---

## Creating a New Repository

### Step-by-Step Guide

**Scenario:** Create a repository for our Review model

**Step 1:** Create the repository

```python
# app/repositories/review_repo.py

from typing import List, Optional
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review
from app.repositories.base import BaseRepository

class ReviewRepository(BaseRepository[Review]):
    """Handles all database operations for reviews"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Review, session)
    
    # Inherits from BaseRepository:
    # - get(id)
    # - get_multi(skip, limit)
    # - create(obj)
    # - update(obj)
    # - delete(id)
    
    # Add review-specific methods:
    
    async def get_by_trip(self, trip_id: int) -> List[Review]:
        """Get all reviews for a specific trip"""
        result = await self.session.execute(
            select(Review)
            .where(Review.trip_id == trip_id)
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_user(self, user_id: str) -> List[Review]:
        """Get all reviews by a specific user"""
        result = await self.session.execute(
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_average_rating(self, trip_id: int) -> float:
        """Calculate average rating for a trip"""
        result = await self.session.execute(
            select(func.avg(Review.rating))
            .where(Review.trip_id == trip_id)
        )
        avg = result.scalar()
        return round(avg, 2) if avg else 0.0
    
    async def user_has_reviewed(self, user_id: str, trip_id: int) -> bool:
        """Check if user already reviewed this trip"""
        result = await self.session.execute(
            select(Review)
            .where(Review.user_id == user_id)
            .where(Review.trip_id == trip_id)
        )
        return result.scalar_one_or_none() is not None
```

**Step 2:** Export it

```python
# app/repositories/__init__.py

# ... existing imports ...
from app.repositories.review_repo import ReviewRepository

__all__ = [
    # ... existing exports ...
    "ReviewRepository",
]
```

### Repository Method Patterns

#### Simple Query (Get one)
```python
async def get_by_email(self, email: str) -> Optional[User]:
    result = await self.session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()
```

#### List Query (Get many)
```python
async def get_by_author(self, author: str) -> List[Book]:
    result = await self.session.execute(
        select(Book).where(Book.author == author)
    )
    return result.scalars().all()
```

#### With Ordering
```python
async def get_recent(self, limit: int = 10) -> List[Post]:
    result = await self.session.execute(
        select(Post)
        .order_by(Post.created_at.desc())  # Newest first
        .limit(limit)
    )
    return result.scalars().all()
```

#### With Pagination
```python
async def get_page(self, page: int = 1, per_page: int = 20) -> List[User]:
    skip = (page - 1) * per_page
    result = await self.session.execute(
        select(User)
        .offset(skip)
        .limit(per_page)
    )
    return result.scalars().all()
```

#### Aggregation
```python
async def count_active_users(self) -> int:
    result = await self.session.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    return result.scalar()
```

#### Search
```python
async def search_by_title(self, term: str) -> List[Book]:
    result = await self.session.execute(
        select(Book).where(Book.title.ilike(f"%{term}%"))  # Case-insensitive
    )
    return result.scalars().all()
```

---

## Common CRUD Operations

### Create (Insert)

```python
# Using repository
async def create_user_example(session: AsyncSession):
    repo = UserRepository(session)
    
    # Create model instance
    new_user = UserProfile(
        id="auth-123",
        username="john_doe",
        email="john@example.com",
        display_name="John Doe"
    )
    
    # Save to database
    user = await repo.create(new_user)
    print(f"Created user with ID: {user.id}")
    return user
```

### Read (Select)

```python
async def read_examples(session: AsyncSession):
    repo = UserRepository(session)
    
    # Get by ID
    user = await repo.get(1)
    
    # Get by unique field
    user = await repo.get_by_email("john@example.com")
    
    # Get multiple (paginated)
    users = await repo.get_multi(skip=0, limit=10)
    
    # Check if exists
    exists = await repo.username_exists("john_doe")
```

### Update

```python
async def update_user_example(session: AsyncSession):
    repo = UserRepository(session)
    
    # Get the user
    user = await repo.get_by_email("john@example.com")
    
    # Modify fields
    user.display_name = "Johnathan Doe"
    user.avatar_url = "https://example.com/avatar.jpg"
    
    # Save changes
    updated_user = await repo.update(user)
    return updated_user
```

### Delete

```python
async def delete_user_example(session: AsyncSession):
    repo = UserRepository(session)
    
    # Delete by ID
    deleted = await repo.delete(1)
    
    if deleted:
        print("User deleted successfully")
    else:
        print("User not found")
```

---

## Summary

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Model** | Define data structure | `class User(SQLModel, table=True)` |
| **Repository** | Database operations | `class UserRepository(BaseRepository)` |
| **async/await** | Handle multiple requests | `user = await repo.get(id)` |
| **Dependency Injection** | Auto-provide resources | `session: AsyncSession = Depends(...)` |
| **Migration** | Track schema changes | `alembic revision --autogenerate` |

---

**Next:** Check out the real code in `app/models/` and `app/repositories/` to see these patterns in action!
