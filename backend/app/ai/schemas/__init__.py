"""AI Schemas module for travel planning."""

from .intent import (
    ExtraNotes,
    TravelIntent,
    QuestionOption,
    ClarificationQuestion,
    ClarificationResponse,
    IntentExtractionError,
)
from .followup import (
    ModificationRequest,
    Suggestion,
    FollowupType,
    FollowupResponse,
)
from .itinerary import (
    ActivityData,
    TripDayData,
    ItineraryOutput,
    ItineraryGenerationError,
)

__all__ = [
    "ExtraNotes",
    "TravelIntent",
    "QuestionOption",
    "ClarificationQuestion",
    "ClarificationResponse",
    "IntentExtractionError",
    "ModificationRequest",
    "Suggestion",
    "FollowupType",
    "FollowupResponse",
    "ActivityData",
    "TripDayData",
    "ItineraryOutput",
    "ItineraryGenerationError",
]
