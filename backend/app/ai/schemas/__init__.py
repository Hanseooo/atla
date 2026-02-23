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
]
