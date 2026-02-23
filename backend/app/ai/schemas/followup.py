"""Schemas for follow-up handler chain."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union


class ModificationRequest(BaseModel):
    """Parsed modification request from user message."""
    
    action: Literal["change", "add", "remove", "extend", "shorten"]
    target: str
    new_value: Optional[Union[str, int, List[str]]] = None
    original_message: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class Suggestion(BaseModel):
    """Destination suggestion for unsure users."""
    
    destination: str
    reason: str
    highlights: List[str] = Field(default_factory=list)
    best_for: List[str] = Field(default_factory=list)
    source: Literal["search", "static"] = "static"


class FollowupType(BaseModel):
    """Classification of follow-up message type."""
    
    type: Literal["clarification", "modification", "new_intent", "unsure", "unknown"]
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class FollowupResponse(BaseModel):
    """Response from follow-up handler."""
    
    type: Literal["clarification", "modification_applied", "suggestions", "complete", "error"]
    updated_intent: Optional["TravelIntent"] = None
    questions: Optional[List["ClarificationQuestion"]] = None
    suggestions: Optional[List[Suggestion]] = None
    message: str
    requires_regeneration: bool = False


from app.ai.schemas.intent import TravelIntent, ClarificationQuestion

FollowupResponse.model_rebuild()
