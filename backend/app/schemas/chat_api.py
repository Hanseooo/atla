from pydantic import BaseModel
from typing import Optional, List, Literal, Any, Dict
from datetime import datetime
from app.ai.schemas.intent import TravelIntent, ClarificationResponse
from app.ai.schemas.itinerary import TripDayData


class ChatRequest(BaseModel):
    """Incoming chat message request."""

    message: str
    session_id: Optional[str] = None


class ItineraryResponse(BaseModel):
    """Response when itinerary is successfully generated.

    Uses the ``ItineraryOutput`` types from the AI chain layer directly,
    without requiring database persistence. DB saving is handled separately.
    """

    type: Literal["itinerary"] = "itinerary"
    session_id: str
    trip_id: Optional[int] = None
    destination: str
    days: int
    budget: Optional[str] = None
    companions: Optional[str] = None
    days_data: List[TripDayData]
    summary: str
    highlights: List[str]
    estimated_cost: Dict[str, Any]
    tips: List[str]
    packing_suggestions: List[str] = []
    message: str


class ErrorResponse(BaseModel):
    """Response when an error occurs."""

    type: Literal["error"] = "error"
    error_code: str
    message: str
    details: Optional[dict] = None
    retry_after: Optional[int] = None


class ChatSession(BaseModel):
    """Session state for chat conversation context."""

    id: str
    user_id: Optional[str] = None
    current_intent: Optional[TravelIntent] = None
    last_clarification: Optional[ClarificationResponse] = None
    created_at: datetime
    updated_at: datetime

