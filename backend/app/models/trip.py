from sqlmodel import SQLModel, Field, Relationship, Column
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


class TripDayDetail(SQLModel):
    day_number: int
    title: str
    trip_date: Optional[date]


class ActivityDetail(SQLModel):
    name: str
    description: Optional[str]
    category: str
    latitude: Optional[float]
    longitude: Optional[float]
    start_time: Optional[str]
    duration_minutes: Optional[int]
