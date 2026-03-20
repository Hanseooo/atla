from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TripListItemResponse(BaseModel):
    id: int
    user_id: str
    title: str
    summary: Optional[str] = None
    destination: str
    days: int
    budget: Optional[str] = None
    travel_style: List[str] = Field(default_factory=list)
    companions: Optional[str] = None
    time_of_year: Optional[str] = None
    total_budget_min: Optional[int] = None
    total_budget_max: Optional[int] = None
    is_public: bool
    view_count: int
    created_from_template_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ActivityResponse(BaseModel):
    id: int
    trip_day_id: int
    name: str
    description: Optional[str] = None
    category: str
    place_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    duration_minutes: Optional[int] = None
    cost_min: Optional[int] = None
    cost_max: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    booking_required: bool
    booking_url: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int
    created_at: datetime


class TripDayResponse(BaseModel):
    id: int
    trip_id: int
    day_number: int
    title: str
    trip_date: Optional[date] = None
    total_cost_min: Optional[int] = None
    total_cost_max: Optional[int] = None
    created_at: datetime
    activities: List[ActivityResponse] = Field(default_factory=list)


class TripDetailResponse(BaseModel):
    id: int
    user_id: str
    title: str
    summary: Optional[str] = None
    destination: str
    days: int
    budget: Optional[str] = None
    travel_style: List[str] = Field(default_factory=list)
    companions: Optional[str] = None
    time_of_year: Optional[str] = None
    total_budget_min: Optional[int] = None
    total_budget_max: Optional[int] = None
    is_public: bool
    view_count: int
    created_from_template_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    trip_days: List[TripDayResponse] = Field(default_factory=list)
