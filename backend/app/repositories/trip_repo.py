from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.trip import Trip, TripDay, Activity
from app.repositories.base import BaseRepository


class TripRepository(BaseRepository[Trip]):
    """Repository for Trip operations"""
    
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
    
    async def get_public_trips(self, skip: int = 0, limit: int = 100) -> List[Trip]:
        """Get public trips ordered by views"""
        result = await self.session.execute(
            select(Trip)
            .where(Trip.is_public == True)
            .order_by(Trip.view_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def increment_views(self, trip_id: int) -> bool:
        """Increment view count for a trip"""
        trip = await self.get(trip_id)
        if trip:
            trip.view_count += 1
            await self.update(trip)
            return True
        return False
    
    async def search_by_destination(
        self, 
        destination: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Search trips by destination"""
        result = await self.session.execute(
            select(Trip)
            .where(Trip.destination.ilike(f"%{destination}%"))
            .where(Trip.is_public == True)
            .order_by(Trip.view_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class TripDayRepository(BaseRepository[TripDay]):
    """Repository for TripDay operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TripDay, session)
    
    async def get_by_trip(self, trip_id: int) -> List[TripDay]:
        """Get all days for a trip"""
        result = await self.session.execute(
            select(TripDay)
            .where(TripDay.trip_id == trip_id)
            .order_by(TripDay.day_number)
        )
        return result.scalars().all()
    
    async def get_with_activities(self, day_id: int) -> Optional[TripDay]:
        """Get day with all activities loaded"""
        result = await self.session.execute(
            select(TripDay)
            .where(TripDay.id == day_id)
            .options(selectinload(TripDay.activities))
        )
        return result.scalar_one_or_none()


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)
    
    async def get_by_trip_day(self, trip_day_id: int) -> List[Activity]:
        """Get all activities for a trip day"""
        result = await self.session.execute(
            select(Activity)
            .where(Activity.trip_day_id == trip_day_id)
            .order_by(Activity.sort_order)
        )
        return result.scalars().all()
    
    async def get_by_category(self, trip_day_id: int, category: str) -> List[Activity]:
        """Get activities by category for a trip day"""
        result = await self.session.execute(
            select(Activity)
            .where(Activity.trip_day_id == trip_day_id)
            .where(Activity.category == category)
            .order_by(Activity.sort_order)
        )
        return result.scalars().all()
    
    async def reorder_activities(self, trip_day_id: int, activity_ids: List[int]) -> bool:
        """Reorder activities by updating sort_order"""
        for index, activity_id in enumerate(activity_ids):
            activity = await self.get(activity_id)
            if activity and activity.trip_day_id == trip_day_id:
                activity.sort_order = index
                await self.session.add(activity)
        
        await self.session.commit()
        return True
