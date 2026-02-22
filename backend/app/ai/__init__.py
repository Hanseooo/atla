"""
AI module for travel planning.

This module contains:
- schemas: Data models for intent extraction and clarification
- prompts: Prompt templates for LLM chains
- chains: LLM chain implementations
- tools: External API integrations (search, weather, geocode, places)
- models: LLM factory and model configurations
"""

from app.ai.schemas import (
    TravelIntent,
    ExtraNotes,
    ClarificationQuestion,
    ClarificationResponse,
    QuestionOption,
)
from app.ai.chains import (
    extract_intent,
    generate_clarification_questions,
    update_intent_from_answers,
)
from app.ai.tools import get_tools, ALL_TOOLS

__all__ = [
    # Schemas
    "TravelIntent",
    "ExtraNotes",
    "ClarificationQuestion",
    "ClarificationResponse",
    "QuestionOption",
    # Chains
    "extract_intent",
    "generate_clarification_questions",
    "update_intent_from_answers",
    # Tools
    "get_tools",
    "ALL_TOOLS",
]