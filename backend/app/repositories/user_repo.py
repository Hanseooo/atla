from typing import List, Optional
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserProfile]):
    """Repository for UserProfile operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(UserProfile, session)
    
    async def get_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user by username (case-insensitive)"""
        result = await self.session.execute(
            select(UserProfile).where(
                func.lower(UserProfile.username) == func.lower(username)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email (case-insensitive)"""
        result = await self.session.execute(
            select(UserProfile).where(
                func.lower(UserProfile.email) == func.lower(email)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID (Supabase auth ID)"""
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def username_exists(self, username: str) -> bool:
        """Check if username already exists (case-insensitive)"""
        result = await self.session.execute(
            select(UserProfile).where(
                func.lower(UserProfile.username) == func.lower(username)
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists (case-insensitive)"""
        result = await self.session.execute(
            select(UserProfile).where(
                func.lower(UserProfile.email) == func.lower(email)
            )
        )
        return result.scalar_one_or_none() is not None
