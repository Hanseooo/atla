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
