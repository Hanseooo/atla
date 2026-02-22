from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class ExtraNotes(BaseModel):
    """Structured personalization notes for trip planning"""
    
    dietary_restrictions: Optional[str] = None
    accessibility_needs: Optional[str] = None
    must_visit: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    special_occasion: Optional[str] = None
    preferred_pace: Optional[Literal["relaxed", "moderate", "packed"]] = "moderate"
    accommodation_type: Optional[Literal["hotel", "resort", "hostel", "airbnb"]] = None
    budget_flexibility: Optional[str] = None
    transport_preference: Optional[Literal["public", "private", "rental"]] = None


class TravelIntent(BaseModel):
    """Structured travel intent extracted from user message"""
    
    destination: Optional[str] = None
    days: Optional[int] = Field(default=None, ge=1, le=30)
    budget: Optional[Literal["low", "mid", "luxury"]] = None
    travel_style: List[Literal["adventure", "relaxation", "culture", "food", "beach", "nature", "nightlife"]] = Field(default_factory=list)
    companions: Optional[Literal["solo", "couple", "family", "group"]] = None
    time_of_year: Optional[str] = None
    
    extra_notes: ExtraNotes = Field(default_factory=ExtraNotes)
    
    missing_info: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        required = ["destination", "days", "budget", "companions"]
        return all(getattr(self, field) for field in required)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields"""
        required = ["destination", "days", "budget", "companions"]
        return [f for f in required if not getattr(self, f)]


class QuestionOption(BaseModel):
    """Single option for choice-based questions"""
    
    id: str
    label: str
    description: Optional[str] = None


class ClarificationQuestion(BaseModel):
    """Single question for user clarification"""
    
    id: str
    field: str
    type: Literal["single_choice", "multiple_choice", "text", "date"]
    question: str
    
    options: Optional[List[QuestionOption]] = None
    
    placeholder: Optional[str] = None
    
    required: bool = True
    priority: int = Field(default=1, ge=1, le=5)


class ClarificationResponse(BaseModel):
    """Response sent to frontend when clarification needed"""
    
    type: Literal["clarification"] = "clarification"
    session_id: Optional[str] = None
    questions: List[ClarificationQuestion]
    current_intent: TravelIntent
    progress: dict
    message: str


class IntentExtractionError(Exception):
    """Custom exception for intent extraction failures"""
    pass
