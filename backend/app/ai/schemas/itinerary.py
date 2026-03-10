"""Schemas for itinerary generation chain."""

from pydantic import BaseModel, Field
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
    activities: List[ActivityData] = Field(default_factory=list)
    meals: Optional[Dict[str, str]] = None
    daily_tips: List[str] = Field(default_factory=list)


class ItineraryOutput(BaseModel):
    """Output from the itinerary generation chain.
    
    This is an intermediate data transfer object used by the chain before
    data is saved to the database. The ChatService converts this into
    SQLModel objects and saves them.
    """

    days_data: List[TripDayData] = Field(default_factory=list)
    summary: str
    highlights: List[str] = Field(default_factory=list)
    estimated_cost: Dict[str, Any] = Field(default_factory=dict)
    tips: List[str] = Field(default_factory=list)
    packing_suggestions: List[str] = Field(default_factory=list)

    # Trip metadata (set from the intent)
    destination: str
    days: int
    budget: Optional[str] = None
    companions: Optional[str] = None
    travel_style: List[str] = Field(default_factory=list)
    time_of_year: Optional[str] = None


class ItineraryGenerationError(Exception):
    """Raised when itinerary generation fails."""
    pass
