"""Schemas for itinerary generation chain."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ActivityData(BaseModel):
    """Data for a single activity in the itinerary."""

    name: str
    description: Optional[str] = None
    category: str = "activity"
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    cost_min: Optional[int] = None
    cost_max: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class TripDayData(BaseModel):
    """Data for a single day in the itinerary."""

    day_number: int
    title: str
    activities: List[ActivityData]
    meals: Optional[Dict[str, str]] = None
    daily_tips: List[str] = []


class ItineraryOutput(BaseModel):
    """Output from the itinerary generation chain.
    
    This is an intermediate data transfer object used by the chain before
    data is saved to the database. The ChatService converts this into
    SQLModel objects and saves them.
    """

    days_data: List[TripDayData]
    summary: str
    highlights: List[str]
    estimated_cost: Dict[str, Any]
    tips: List[str]
    packing_suggestions: List[str] = []

    # Trip metadata (set from the intent)
    destination: str
    days: int
    budget: Optional[str] = None
    companions: Optional[str] = None
    travel_style: List[str] = []
    time_of_year: Optional[str] = None


class ItineraryGenerationError(Exception):
    """Raised when itinerary generation fails."""
    pass
