from typing import List, Optional
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.place import Place, SavedPlace
from app.repositories.base import BaseRepository


class PlaceRepository(BaseRepository[Place]):
    """Repository for Place operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Place, session)
    
    async def get_by_name(self, name: str) -> Optional[Place]:
        """Get place by exact name match"""
        result = await self.session.execute(
            select(Place).where(Place.name == name)
        )
        return result.scalar_one_or_none()
    
    async def search_by_name(self, search_term: str, limit: int = 20) -> List[Place]:
        """Search places by name (partial match)"""
        result = await self.session.execute(
            select(Place)
            .where(Place.name.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_category(self, category: str, limit: int = 100) -> List[Place]:
        """Get all places in a category"""
        result = await self.session.execute(
            select(Place)
            .where(Place.category == category)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_nearby(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float = 10.0,
        limit: int = 20
    ) -> List[Place]:
        """Get places within radius using approximate bounding box"""
        # Convert km to degrees (approximate)
        lat_delta = radius_km / 111.0  # 1 degree lat ≈ 111 km
        lon_delta = radius_km / (111.0 * abs(func.cos(func.radians(lat))))
        
        result = await self.session.execute(
            select(Place)
            .where(Place.latitude.between(lat - lat_delta, lat + lat_delta))
            .where(Place.longitude.between(lon - lon_delta, lon + lon_delta))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_top_rated(self, limit: int = 10) -> List[Place]:
        """Get top rated places"""
        result = await self.session.execute(
            select(Place)
            .where(Place.rating.isnot(None))
            .order_by(Place.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()


class SavedPlaceRepository(BaseRepository[SavedPlace]):
    """Repository for SavedPlace operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(SavedPlace, session)
    
    async def get_by_user(self, user_id: str) -> List[SavedPlace]:
        """Get all places saved by a user"""
        result = await self.session.execute(
            select(SavedPlace)
            .where(SavedPlace.user_id == user_id)
            .order_by(SavedPlace.created_at.desc())
        )
        return result.scalars().all()
    
    async def is_saved(self, user_id: str, place_id: str) -> bool:
        """Check if a place is saved by a user"""
        result = await self.session.execute(
            select(SavedPlace)
            .where(SavedPlace.user_id == user_id)
            .where(SavedPlace.place_id == place_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def unsave(self, user_id: str, place_id: str) -> bool:
        """Remove a saved place"""
        result = await self.session.execute(
            select(SavedPlace)
            .where(SavedPlace.user_id == user_id)
            .where(SavedPlace.place_id == place_id)
        )
        saved = result.scalar_one_or_none()
        if saved:
            await self.session.delete(saved)
            await self.session.commit()
            return True
        return False
