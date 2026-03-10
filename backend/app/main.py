from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.api import auth
from app.api import chat

app = FastAPI(
    title="Philippine Travel API",
    description="AI-powered travel planning API for the Philippines",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """Health check endpoint that verifies database connectivity"""
    try:
        # Execute a simple query to verify database connection
        result = await session.execute(text("SELECT 1"))
        result.fetchone()
        
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "database": "connected",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "environment": settings.ENVIRONMENT,
                "database": "disconnected",
                "error": str(e),
            },
        )


@app.get("/")
async def root():
    return {
        "message": "Philippine Travel API",
        "docs": "/docs",
        "health": "/health",
    }
