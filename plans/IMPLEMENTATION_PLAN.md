# AI Agent Implementation Plan

**Project:** Atla - Philippine AI Travel Planner  
**Scope:** Backend AI Agent (Issues #5-#9)  
**Architecture:** Pure LangChain (no LangGraph)  
**Last Updated:** February 2026

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Models](#data-models)
3. [Implementation Phases](#implementation-phases)
4. [File Structure](#file-structure)
5. [Edge Cases & Error Handling](#edge-cases--error-handling)
6. [API Contracts](#api-contracts)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Checklist](#deployment-checklist)

---

## Architecture Overview

### System Flow

```
User Message
    ↓
[Chat API Endpoint]
    ↓
ChatService (Orchestrator)
    ↓
Intent Extraction Chain
    ├─ Complete? → Itinerary Generation Chain → Save to DB
    └─ Incomplete? → Generate Questions → Return Clarification
    ↓
Return Response
```

> **Note:** Redis session management will be added in a future phase. Current MVP is stateless.

### Key Decisions

1. **Pure LangChain**: Simpler implementation, easier debugging, faster MVP
2. **Error handling (Approach A)**: Return empty intent on failure, trigger clarification flow
3. **Predefined extra_notes**: Structured data for reliable personalization
4. **No conditional questions**: Flat question list for MVP simplicity
5. **DuckDuckGo for dev**: Using DDG search during development; Brave Search for production

---

## Data Models

### 1. TravelIntent

```python
class TravelIntent(BaseModel):
    """Structured travel intent extracted from user message"""
    
    # Core fields
    destination: Optional[str] = None
    days: Optional[int] = Field(None, ge=1, le=30)
    budget: Optional[Literal["low", "mid", "luxury"]] = None
    travel_style: List[Literal["adventure", "relaxation", "culture", "food", "beach", "nature", "nightlife"]] = []
    companions: Optional[Literal["solo", "couple", "family", "group"]] = None
    time_of_year: Optional[str] = None  # "December 2024", "next week"
    
    # Personalization
    extra_notes: ExtraNotes = Field(default_factory=ExtraNotes)
    
    # Metadata
    missing_info: List[str] = []  # List of missing field names
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        required = ["destination", "days", "budget", "companions"]
        return all(getattr(self, field) for field in required)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing required fields"""
        required = ["destination", "days", "budget", "companions"]
        return [f for f in required if not getattr(self, f)]


class ExtraNotes(BaseModel):
    """Structured personalization notes"""
    
    dietary_restrictions: Optional[str] = None  # "vegetarian, halal, allergies"
    accessibility_needs: Optional[str] = None  # "wheelchair, elderly-friendly"
    must_visit: List[str] = []  # ["Chocolate Hills", "Tarsier Sanctuary"]
    avoid: List[str] = []  # ["crowded places", "hiking"]
    interests: List[str] = []  # ["photography", "local food", "history"]
    special_occasion: Optional[str] = None  # "honeymoon", "anniversary", "birthday"
    preferred_pace: Optional[Literal["relaxed", "moderate", "packed"]] = "moderate"
    accommodation_type: Optional[Literal["hotel", "resort", "hostel", "airbnb"]] = None
    budget_flexibility: Optional[str] = None  # "strict", "flexible for experiences"
    transport_preference: Optional[Literal["public", "private", "rental"]] = None
```

### 2. ClarificationQuestion

```python
class QuestionOption(BaseModel):
    """Single option for choice-based questions"""
    id: str  # Machine-readable ID
    label: str  # Human-readable label
    description: Optional[str] = None  # Additional context


class ClarificationQuestion(BaseModel):
    """Single question for user clarification"""
    
    id: str  # Unique question ID
    field: str  # Which TravelIntent field this answers
    type: Literal["single_choice", "multiple_choice", "text", "date"]
    question: str  # The actual question text
    
    # For choice types
    options: Optional[List[QuestionOption]] = None
    
    # For text input
    placeholder: Optional[str] = None
    
    # UI hints
    required: bool = True
    priority: int = Field(1, ge=1, le=5)  # 1 = highest


class ClarificationResponse(BaseModel):
    """Response sent to frontend when clarification needed"""
    
    type: Literal["clarification"] = "clarification"
    session_id: Optional[str] = None  # Set by ChatService when available
    questions: List[ClarificationQuestion]
    current_intent: TravelIntent  # Partial intent state
    progress: dict  # { "completed": 3, "total": 4, "percentage": 75 }
    message: str  # Friendly message like "I need a bit more info..."
```

### 3. ChatResponse (Itinerary)

```python
class ItineraryResponse(BaseModel):
    """Response when itinerary successfully generated"""
    
    type: Literal["itinerary"] = "itinerary"
    session_id: str
    trip: Trip  # SQLModel Trip object
    days: List[TripDay]
    activities: List[Activity]
    summary: str  # Human-readable summary
    highlights: List[str]  # Key highlights
    estimated_cost: dict  # { "min": 15000, "max": 25000, "currency": "PHP" }
    tips: List[str]  # Travel tips based on extra_notes
    message: str  # Friendly completion message


class ErrorResponse(BaseModel):
    """Error response"""
    
    type: Literal["error"] = "error"
    error_code: str  # "VALIDATION_ERROR", "LLM_TIMEOUT", "API_ERROR"
    message: str  # User-friendly error message
    details: Optional[dict] = None  # Debug info (dev only)
    retry_after: Optional[int] = None  # For rate limiting
```

---

## Implementation Phases

### Phase 1: Foundation Tools (Issue #8) - ✅ COMPLETE

**Goal:** Create all tools needed by chains

#### 1.1 Tool Implementations

**DuckDuckGo Search Tool** (Development)
```python
# app/ai/tools/duckduckgo_search.py
@tool
async def duckduckgo_search(
    query: str,
    region: str = "ph-ph",
    max_results: int = 5,
) -> str:
    """
    Search for travel information using DuckDuckGo.
    
    Args:
        query: Search query (e.g., "best beaches in Cebu")
        region: Region code for localized results (default: "ph-ph" for Philippines)
        max_results: Maximum number of results to return (default: 5, max: 10)
    
    Returns:
        Markdown-formatted search results with titles, snippets, and URLs.
    """
    # Uses ddgs library wrapped in asyncio.to_thread()
```

> **Note:** DuckDuckGo is used during development. Brave Search (`brave_web_search.py` placeholder) will be used in production.

**Weather Tool**
```python
# app/ai/tools/weather.py
@tool
async def get_weather(
    location: str,
    date: Optional[str] = None,
    units: str = "metric",
) -> str:
    """
    Get weather forecast for a location using OpenWeather API.
    
    Only provides forecast data if the requested date is within 5 days from now.
    For dates beyond 5 days, returns current weather only.

    Args:
        location: City name (e.g., "Cebu", "Manila", "Boracay")
        date: Target date in YYYY-MM-DD format (optional)
        units: Temperature units - "metric" (Celsius) or "imperial" (Fahrenheit)

    Returns:
        Weather summary with temperature, conditions, and travel recommendations.
    """
    # OpenWeather API integration with date-only comparison for accuracy
```

**Places Search Tool**
```python
# app/ai/tools/search_places.py
@tool
async def search_places(
    latitude: float,
    longitude: float,
    radius: int = 5000,
    categories: str = "catering,tourism,entertainment",
    limit: int = 20,
) -> str:
    """
    Search for places near a location using Geoapify Places API.

    Args:
        latitude: Latitude of search center
        longitude: Longitude of search center
        radius: Search radius in meters (default: 5000 = 5km)
        categories: Comma-separated categories
        limit: Maximum number of results (default: 20, max: 100)

    Returns:
        Formatted markdown with places grouped by category.
    """
    # Geoapify Places API with rich formatting
```

**Geocode Tool**
```python
# app/ai/tools/geocode.py
@tool
async def geocode(query: str) -> str:
    """
    Geocode a location to get its latitude and longitude.

    Args:
        query: Location to geocode (e.g., "Manila", "Rizal Park")

    Returns:
        Coordinates in "latitude,longitude" format, or error message.
    """
    # Geoapify Geocoding API
```

#### 1.2 Tool Registry

```python
# app/ai/tools/__init__.py
from typing import List, Callable

from .duckduckgo_search import duckduckgo_search
from .geocode import geocode
from .search_places import search_places
from .weather import get_weather

ALL_TOOLS: List[Callable] = [
    duckduckgo_search,
    geocode,
    search_places,
    get_weather,
]

def get_tools() -> List[Callable]:
    """Get all available AI tools."""
    return ALL_TOOLS
```

#### 1.3 Future Enhancements

**Base Tool Class with Error Handling** (Not yet implemented)
```python
# app/ai/tools/base.py - Future Enhancement
class BaseTool(ABC):
    """Base class for all AI tools with error handling"""
    
    name: str
    description: str
    max_retries: int = 3
    timeout: float = 10.0
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def execute(self, **kwargs) -> Any:
        """Execute tool with retry logic"""
        pass
```

**Centralized Error Handler** (Not yet implemented)
```python
# app/ai/tools/error_handler.py - Future Enhancement
class ToolErrorHandler:
    """Centralized error handling for tools"""
    
    @staticmethod
    def handle_error(tool_name: str, error: Exception) -> dict:
        """Convert exception to user-friendly response"""
        pass
```

**Success Criteria:**
- [x] 4 tools implemented with `@tool` decorator
- [x] Async/await throughout
- [x] Graceful error handling (return error strings on failure)
- [x] Type annotations for tool registry
- [ ] Retry logic with exponential backoff (Future Enhancement)
- [ ] Caching layer (Future Enhancement)
- [ ] Unit tests for each tool

---

### Phase 2: Intent Extraction (Issue #5) - ✅ COMPLETE

**Goal:** Extract structured intent from natural language

#### 2.1 Prompt Template

```python
# app/ai/prompts/intent_extraction.py
INTENT_EXTRACTION_PROMPT = """You are an expert travel planning assistant for the Philippines...

{format_instructions}
"""

QUESTION_TEMPLATES = {
    "destination": {
        "question": "Where in the Philippines would you like to visit?",
        "type": "text",
        "placeholder": "e.g., Cebu, Boracay, Palawan, Baguio",
    },
    "days": {
        "question": "How many days is your trip?",
        "type": "single_choice",
        "options": [
            {"id": "3", "label": "Weekend trip (2-3 days)"},
            {"id": "5", "label": "Short getaway (4-5 days)"},
            # ...
        ],
    },
    # ... more templates
}

PROGRESS_MESSAGES = {
    0: "I'd love to help you plan your trip! Let me get some details first.",
    1: "Great start! Just a few more questions...",
    2: "Almost there! One more thing...",
    3: "Perfect! Let me put together your itinerary...",
}
```

#### 2.2 Chain Implementation

```python
# app/ai/chains/intent_extraction.py
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from app.ai.models.llms.gemini import LLMFactory
from app.ai.schemas.intent import TravelIntent

CONFIDENCE_THRESHOLD = 0.7


async def extract_intent(
    message: str,
    user_context: Optional[dict] = None,
) -> TravelIntent:
    """
    Extract travel intent from user message.

    Args:
        message: User's natural language message
        user_context: Optional user preferences from database

    Returns:
        TravelIntent object with extracted data.
        Returns empty intent with confidence=0.0 on failure.
    """
    try:
        llm = LLMFactory.create_llm(
            model_name="gemini-2.5-flash-lite",
            temp=0.1,
        )

        parser = PydanticOutputParser(pydantic_object=TravelIntent)

        prompt = PromptTemplate(
            template=INTENT_EXTRACTION_PROMPT,
            input_variables=["message", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm

        context_str = json.dumps(user_context) if user_context else "No previous context"

        result = await chain.ainvoke({
            "message": message,
            "context": context_str,
        })

        result_text = result.content if hasattr(result, "content") else str(result)

        intent = await _parse_intent(result_text, parser)

        intent.missing_info = intent.get_missing_fields()

        return intent

    except Exception as e:
        logger.error(f"Intent extraction failed: {e}", exc_info=True)
        return TravelIntent(
            missing_info=["destination", "days", "budget", "companions"],
            confidence=0.0,
        )


async def _parse_intent(text: str, parser: PydanticOutputParser) -> TravelIntent:
    """Parse LLM output into TravelIntent with fallback handling."""
    
    try:
        return parser.parse(text)
    except Exception:
        pass

    # Fallback: Try to extract JSON manually
    try:
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            data = json.loads(json_match.group())
            return TravelIntent(**data)
    except Exception:
        pass

    return TravelIntent(
        missing_info=["destination", "days", "budget", "companions"],
        confidence=0.0,
    )


def generate_clarification_questions(
    intent: TravelIntent,
    max_questions: int = 3,
) -> ClarificationResponse:
    """Generate questions for missing required fields."""
    # Implementation uses QUESTION_TEMPLATES
    pass


def update_intent_from_answers(
    intent: TravelIntent,
    answers: dict,
) -> TravelIntent:
    """Update intent based on user's clarification answers."""
    # Implementation merges answers into existing intent
    pass
```

**Error Handling Approach (Approach A):**
- Returns empty `TravelIntent` with `confidence=0.0` on any failure
- ChatService checks `intent.confidence < 0.7` to prompt user to rephrase
- Triggers clarification questions for missing fields

**Success Criteria:**
- [x] Extracts all 4 required fields accurately
- [x] Parses extra_notes into structured dict
- [x] Handles unclear messages gracefully (returns empty intent)
- [x] Returns confidence score
- [x] < 2 second response time
- [x] Generates clarification questions for missing fields
- [x] Updates intent from user answers

---

### Phase 3: Clarification Questions (Part of Issue #5) - ✅ COMPLETE

**Goal:** Generate UI-friendly questions for missing info

> **Note:** Clarification logic is implemented in `app/ai/chains/intent_extraction.py` alongside intent extraction.

#### 3.1 Question Templates

```python
# app/ai/prompts/intent_extraction.py
QUESTION_TEMPLATES = {
    "destination": {
        "question": "Where in the Philippines would you like to visit?",
        "type": "text",
        "placeholder": "e.g., Cebu, Boracay, Palawan, Baguio"
    },
    "days": {
        "question": "How many days is your trip?",
        "type": "single_choice",
        "options": [
            {"id": "3", "label": "Weekend trip (2-3 days)"},
            {"id": "5", "label": "Short getaway (4-5 days)"},
            {"id": "7", "label": "Week-long vacation (6-7 days)"},
            {"id": "10", "label": "Extended trip (8-10 days)"},
            {"id": "14", "label": "Two weeks+"},
        ]
    },
    "budget": {
        "question": "What's your budget range?",
        "type": "single_choice",
        "options": [
            {"id": "low", "label": "Budget-friendly", "description": "Under P5,000/day"},
            {"id": "mid", "label": "Moderate", "description": "P5,000-15,000/day"},
            {"id": "luxury", "label": "Luxury", "description": "P15,000+/day"},
        ]
    },
    "companions": {
        "question": "Who are you traveling with?",
        "type": "single_choice",
        "options": [
            {"id": "solo", "label": "Solo", "description": "Just me"},
            {"id": "couple", "label": "Partner", "description": "With my significant other"},
            {"id": "family", "label": "Family", "description": "With kids/relatives"},
            {"id": "group", "label": "Group", "description": "Friends or tour group"},
        ]
    },
    "travel_style": {
        "question": "What activities interest you? (Choose all that apply)",
        "type": "multiple_choice",
        "options": [
            {"id": "beach", "label": "Beach & Water"},
            {"id": "adventure", "label": "Adventure"},
            {"id": "culture", "label": "Culture & History"},
            {"id": "food", "label": "Food & Dining"},
            {"id": "nature", "label": "Nature & Wildlife"},
            {"id": "relaxation", "label": "Relaxation"},
            {"id": "nightlife", "label": "Nightlife"},
        ]
    },
    "time_of_year": {
        "question": "When are you planning to travel?",
        "type": "text",
        "placeholder": "e.g., December 2024, next month, summer"
    }
}


def generate_clarification_questions(
    intent: TravelIntent,
    max_questions: int = 3,
) -> ClarificationResponse:
    """
    Generate questions for missing required fields.
    
    Args:
        intent: Partial TravelIntent
        max_questions: Maximum questions to ask at once
    
    Returns:
        ClarificationResponse with questions and current state
    """
    missing = intent.get_missing_fields()

    priority_order = ["destination", "days", "budget", "companions", "travel_style", "time_of_year"]
    missing.sort(key=lambda x: priority_order.index(x) if x in priority_order else 999)

    to_ask = missing[:max_questions]

    questions = []
    for field in to_ask:
        template = QUESTION_TEMPLATES.get(field)
        if template:
            questions.append(ClarificationQuestion(
                id=f"q_{field}",
                field=field,
                type=template["type"],
                question=template["question"],
                options=[QuestionOption(**opt) for opt in template.get("options", [])],
                placeholder=template.get("placeholder"),
                priority=priority_order.index(field) + 1,
            ))

    total_required = 4
    completed = total_required - len(missing)

    return ClarificationResponse(
        session_id=None,
        questions=questions,
        current_intent=intent,
        progress={
            "completed": completed,
            "total": total_required,
            "percentage": int((completed / total_required) * 100),
        },
        message=PROGRESS_MESSAGES.get(completed, "Let's continue planning your adventure!"),
    )
```

**Success Criteria:**
- [x] Generates max 3 questions at a time
- [x] Prioritizes required fields correctly
- [x] Returns proper UI types (choice vs text)
- [x] Calculates progress percentage

---

### Phase 4: Itinerary Generation (Issue #6) - Priority: Critical

**Goal:** Generate complete day-by-day itinerary

#### 4.1 Prompt Template

```python
# app/ai/prompts/itinerary_generation.py
ITINERARY_GENERATION_PROMPT = """
You are an expert Philippine travel planner. Create a detailed day-by-day itinerary based on the user's preferences.

USER PREFERENCES:
Destination: {destination}
Duration: {days} days
Budget: {budget}
Traveling with: {companions}
Style: {travel_style}
When: {time_of_year}

PERSONALIZATION NOTES:
{extra_notes}

AVAILABLE PLACES DATA:
{places_data}

WEATHER FORECAST:
{weather_data}

Create an itinerary following these rules:

1. DAILY STRUCTURE:
   - Each day should have 3-5 activities
   - Mix of must-see attractions and local experiences
   - Include meal recommendations (breakfast, lunch, dinner)
   - Consider travel time between locations
   - Start and end at reasonable times (not too early/late)

2. BUDGET CONSIDERATIONS:
   - Low: Street food, public transport, free attractions, hostels
   - Mid: Mix of restaurants and street food, some paid attractions, mid-range hotels
   - Luxury: Fine dining, private tours, all top attractions, resorts

3. COMPANION ADJUSTMENTS:
   - Solo: Safe areas, social activities, easy to navigate
   - Couple: Romantic spots, couple activities, nice restaurants
   - Family: Kid-friendly, shorter activity durations, family rooms
   - Group: Group discounts, activities for various interests

4. PERSONALIZATION:
   - Incorporate must_visit places
   - Respect dietary_restrictions for restaurant choices
   - Include accessibility_needs considerations
   - Match preferred_pace (relaxed/moderate/packed)

5. PRACTICAL DETAILS:
   - Include estimated costs per activity
   - Note opening hours
   - Suggest best times to visit
   - Include transportation tips

Respond with a JSON object:
{{
    "summary": "Brief overview of the trip",
    "highlights": ["Key highlight 1", "Key highlight 2"],
    "days": [
        {{
            "day_number": 1,
            "title": "Day 1: Arrival and City Tour",
            "date": "2024-12-01",
            "activities": [
                {{
                    "name": "Activity name",
                    "description": "What to do",
                    "category": "attraction|restaurant|transport|activity",
                    "start_time": "09:00",
                    "duration_minutes": 120,
                    "cost_min": 0,
                    "cost_max": 500,
                    "place_id": "optional_reference_to_places_db"
                }}
            ],
            "meals": {{
                "breakfast": "Suggestion",
                "lunch": "Suggestion",
                "dinner": "Suggestion"
            }},
            "daily_tips": ["Tip 1", "Tip 2"]
        }}
    ],
    "estimated_cost": {{
        "accommodation": {{"min": 2000, "max": 5000, "per_night": true}},
        "activities": {{"min": 3000, "max": 8000}},
        "food": {{"min": 1500, "max": 4000, "per_day": true}},
        "transport": {{"min": 1000, "max": 3000}},
        "total_min": 15000,
        "total_max": 35000
    }},
    "general_tips": ["Tip 1", "Tip 2"],
    "packing_suggestions": ["Item 1", "Item 2"]
}}
"""
```

#### 4.2 Chain Implementation

```python
# app/ai/chains/itinerary_generation.py
from langchain import LLMChain, PromptTemplate
import json

async def generate_itinerary(
    intent: TravelIntent,
    tools: List[Callable]
) -> ItineraryOutput:
    """
    Generate complete itinerary from travel intent.
    
    Args:
        intent: Complete TravelIntent object
        tools: List of available tools
    
    Returns:
        ItineraryOutput with trip, days, and activities
    """
    try:
        # Step 1: Gather data using tools
        places_data = await _gather_places_data(intent, tools)
        weather_data = await _gather_weather_data(intent, tools)
        
        # Step 2: Generate raw itinerary with LLM
        llm = LLMFactory.create_llm(temp=0.7)  # Higher temp for creativity
        
        prompt = PromptTemplate(
            template=ITINERARY_GENERATION_PROMPT,
            input_variables=[
                "destination", "days", "budget", "companions",
                "travel_style", "time_of_year", "extra_notes",
                "places_data", "weather_data"
            ]
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        result = await chain.ainvoke({
            "destination": intent.destination,
            "days": intent.days,
            "budget": intent.budget,
            "companions": intent.companions,
            "travel_style": ", ".join(intent.travel_style),
            "time_of_year": intent.time_of_year or "Not specified",
            "extra_notes": json.dumps(intent.extra_notes.dict(), indent=2),
            "places_data": places_data,
            "weather_data": weather_data
        })
        
        # Step 3: Parse and validate
        raw_itinerary = json.loads(result["text"])
        
        # Step 4: Post-process to ensure personalization
        validated = await _validate_against_preferences(raw_itinerary, intent)
        
        # Step 5: Convert to database models
        itinerary_output = await _convert_to_models(validated, intent)
        
        return itinerary_output
        
    except Exception as e:
        logger.error(f"Itinerary generation failed: {e}", exc_info=True)
        raise ItineraryGenerationError(f"Failed to generate itinerary: {str(e)}")


async def _gather_places_data(intent: TravelIntent, tools: List[Callable]) -> str:
    """Gather places information using tools"""
    # Query places DB
    # Use search tools
    # Format results
    pass


async def _validate_against_preferences(
    itinerary: dict,
    intent: TravelIntent
) -> dict:
    """Ensure itinerary respects extra_notes preferences"""
    notes = intent.extra_notes
    
    # Validate must_visit places are included
    if notes.must_visit:
        # Check each must_visit is in itinerary
        # If not, add or swap activities
        pass
    
    # Filter out avoided items
    if notes.avoid:
        # Remove activities matching avoid list
        pass
    
    # Adjust for dietary restrictions
    if notes.dietary_restrictions:
        # Ensure restaurants accommodate restrictions
        pass
    
    # Adjust pace
    if notes.preferred_pace == "relaxed":
        # Reduce number of activities per day
        pass
    elif notes.preferred_pace == "packed":
        # Add more activities
        pass
    
    return itinerary


async def _convert_to_models(
    itinerary: dict,
    intent: TravelIntent
) -> ItineraryOutput:
    """Convert raw itinerary to SQLModel objects"""
    # Create Trip object
    trip = Trip(
        user_id=intent.user_id if hasattr(intent, 'user_id') else None,
        title=f"{intent.days}-Day Trip to {intent.destination}",
        summary=itinerary["summary"],
        destination=intent.destination,
        days=intent.days,
        budget=intent.budget,
        travel_style=intent.travel_style,
        companions=intent.companions,
        time_of_year=intent.time_of_year,
        total_budget_min=itinerary["estimated_cost"]["total_min"],
        total_budget_max=itinerary["estimated_cost"]["total_max"]
    )
    
    # Create TripDays and Activities
    days = []
    activities = []
    
    for day_data in itinerary["days"]:
        trip_day = TripDay(
            day_number=day_data["day_number"],
            title=day_data["title"],
            trip_date=day_data.get("date")
        )
        days.append(trip_day)
        
        for act_data in day_data["activities"]:
            activity = Activity(
                name=act_data["name"],
                description=act_data["description"],
                category=act_data["category"],
                start_time=act_data.get("start_time"),
                duration_minutes=act_data.get("duration_minutes"),
                cost_min=act_data.get("cost_min"),
                cost_max=act_data.get("cost_max")
            )
            activities.append(activity)
    
    return ItineraryOutput(
        trip=trip,
        days=days,
        activities=activities,
        summary=itinerary["summary"],
        highlights=itinerary["highlights"],
        estimated_cost=itinerary["estimated_cost"],
        tips=itinerary["general_tips"]
    )
```

**Success Criteria:**
- [ ] Generates complete itinerary with all days
- [ ] Includes 3-5 activities per day
- [ ] Respects all extra_notes preferences
- [ ] Provides cost estimates
- [ ] Includes practical tips
- [ ] < 10 second generation time

---

### Phase 5: Follow-up Handler (Issue #7)

**Goal:** Handle clarification responses and modifications

```python
# app/ai/chains/followup_handler.py

async def update_intent_from_answers(
    intent: TravelIntent,
    answers: dict  # {question_id: answer_value}
) -> TravelIntent:
    """
    Update intent based on user's clarification answers.
    
    Args:
        intent: Current partial intent
        answers: Dictionary of question_id -> answer
    
    Returns:
        Updated TravelIntent
    """
    updated_intent = intent.copy(deep=True)
    
    for question_id, answer in answers.items():
        field = question_id.replace("q_", "")  # Extract field name
        
        if field == "destination":
            updated_intent.destination = answer
        elif field == "days":
            updated_intent.days = int(answer)
        elif field == "budget":
            updated_intent.budget = answer
        elif field == "companions":
            updated_intent.companions = answer
        elif field == "travel_style":
            # Handle multiple choice
            if isinstance(answer, list):
                updated_intent.travel_style = answer
            else:
                updated_intent.travel_style = [answer]
        elif field == "time_of_year":
            updated_intent.time_of_year = answer
    
    # Recalculate missing fields
    updated_intent.missing_info = updated_intent.get_missing_fields()
    
    return updated_intent


async def handle_modification_request(
    current_intent: TravelIntent,
    current_itinerary: Optional[ItineraryOutput],
    modification_request: str
) -> dict:
    """
    Handle user request to modify existing itinerary.
    
    Args:
        current_intent: Current travel intent
        current_itinerary: Existing itinerary (if any)
        modification_request: User's modification message
    
    Returns:
        Dict with action type and updated data
    """
    # Use LLM to understand modification
    # Examples:
    # - "Can you make it 5 days instead of 3?" → update days, regenerate
    # - "I don't like the beach activities" → remove beach, regenerate
    # - "Add more food tours" → update travel_style, regenerate
    
    pass
```

---

### Phase 6: Chat Service & API (Issue #9) - Priority: Critical

**Goal:** Orchestrate all components and expose API

#### 6.1 Chat Service

```python
# app/services/chat_service.py
from redis.asyncio import Redis
from langchain.memory import RedisChatMessageHistory

class ChatService:
    """Main orchestrator for chat interactions"""
    
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.session_ttl = 600  # 10 minutes
        self.cleanup_delay = 120  # 2 minutes after completion
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Union[ClarificationResponse, ItineraryResponse, ErrorResponse]:
        """
        Main entry point for processing chat messages.
        
        Flow:
        1. Load or create session
        2. Extract intent from message
        3. Check if complete
        4. If incomplete → generate clarification questions
        5. If complete → generate itinerary
        6. Save to database
        7. Schedule cleanup
        """
        try:
            # Step 1: Session management
            session = await self._get_or_create_session(session_id, user_id)
            
            # Step 2: Load user preferences if authenticated
            user_context = None
            if user_id:
                user_context = await self._load_user_preferences(user_id)
            
            # Step 3: Extract intent
            intent = await extract_intent(message, user_context)
            
            # Step 4: Merge with existing intent if clarification
            if session.current_intent:
                intent = await self._merge_intents(session.current_intent, intent)
            
            # Step 5: Check completeness
            if not intent.is_complete():
                # Generate clarification questions
                clarification = await generate_clarification_questions(intent)
                clarification.session_id = session.id
                
                # Save partial intent to Redis
                await self._save_session(session, intent, clarification)
                
                return clarification
            
            # Step 6: Generate itinerary
            itinerary = await generate_itinerary(intent)
            
            # Step 7: Save to database
            await self._save_itinerary_to_db(itinerary, user_id)
            
            # Step 8: Schedule Redis cleanup
            await self._schedule_cleanup(session.id)
            
            return ItineraryResponse(
                type="itinerary",
                session_id=session.id,
                trip=itinerary.trip,
                days=itinerary.days,
                activities=itinerary.activities,
                summary=itinerary.summary,
                highlights=itinerary.highlights,
                estimated_cost=itinerary.estimated_cost,
                tips=itinerary.tips,
                message="Your itinerary is ready! 🎉"
            )
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}", exc_info=True)
            return ErrorResponse(
                type="error",
                error_code="PROCESSING_ERROR",
                message="I'm having trouble understanding your request. Could you try rephrasing?"
            )
    
    async def _get_or_create_session(
        self,
        session_id: Optional[str],
        user_id: Optional[str]
    ) -> ChatSession:
        """Get existing session or create new one"""
        if session_id:
            # Try to load from Redis
            data = await self.redis.get(f"chat:{session_id}")
            if data:
                return ChatSession.parse_raw(data)
        
        # Create new session
        return ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow()
        )
    
    async def _save_session(
        self,
        session: ChatSession,
        intent: TravelIntent,
        clarification: ClarificationResponse
    ):
        """Save session to Redis"""
        session.current_intent = intent
        session.last_clarification = clarification
        session.updated_at = datetime.utcnow()
        
        await self.redis.setex(
            f"chat:{session.id}",
            self.session_ttl,
            session.json()
        )
    
    async def _schedule_cleanup(self, session_id: str):
        """Schedule Redis cleanup after delay"""
        # Use Redis delayed execution or Celery
        # For simplicity, just set shorter TTL
        await self.redis.expire(f"chat:{session_id}", self.cleanup_delay)
```

#### 6.2 API Endpoints

```python
# app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.chat_service import ChatService
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/", response_model=Union[ClarificationResponse, ItineraryResponse])
async def chat(
    request: ChatRequest,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
):
    """
    Process chat message and return response.
    
    Returns clarification questions if info missing,
    or complete itinerary if all info provided.
    """
    service = ChatService()
    
    response = await service.process_message(
        message=request.message,
        session_id=request.session_id,
        user_id=current_user.id if current_user else None
    )
    
    if response.type == "error":
        raise HTTPException(status_code=400, detail=response.message)
    
    return response


@router.post("/{session_id}/clarify")
async def submit_clarification(
    session_id: str,
    answers: dict,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
):
    """Submit answers to clarification questions"""
    service = ChatService()
    
    # Load session
    # Update intent with answers
    # Check completeness again
    # Return clarification or itinerary
    pass


@router.get("/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
):
    """Get chat session history"""
    # Load from Redis
    # If not in Redis, return 404
    pass
```

---

## File Structure

### Current Implementation

```
backend/app/ai/
├── __init__.py                 # Exports schemas, chains, tools
├── chains/
│   ├── __init__.py
│   └── intent_extraction.py    # extract_intent, generate_clarification_questions, update_intent_from_answers
├── models/
│   ├── __init__.py
│   └── llms/
│       ├── __init__.py
│       └── gemini.py           # LLMFactory for Gemini models
├── prompts/
│   ├── __init__.py
│   └── intent_extraction.py    # INTENT_EXTRACTION_PROMPT, QUESTION_TEMPLATES, PROGRESS_MESSAGES
├── schemas/
│   ├── __init__.py
│   └── intent.py               # TravelIntent, ExtraNotes, ClarificationQuestion, ClarificationResponse
└── tools/
    ├── __init__.py             # get_tools(), ALL_TOOLS
    ├── duckduckgo_search.py    # DuckDuckGo search (dev)
    ├── brave_web_search.py     # Placeholder for production
    ├── geocode.py              # Geoapify geocoding
    ├── search_places.py        # Geoapify places search
    └── weather.py              # OpenWeather API
```

### Future Files (Not Yet Implemented)

```
backend/app/ai/
├── chains/
│   ├── itinerary_generation.py # Issue #6
│   └── followup_handler.py     # Issue #7
├── prompts/
│   └── itinerary_generation.py # Issue #6
├── tools/
│   ├── base.py                 # Future: BaseTool class with retry logic
│   ├── error_handler.py        # Future: Centralized error handling
│   └── circuit_breaker.py      # Future: Circuit breaker pattern

backend/app/
├── services/
│   └── chat_service.py         # Issue #9
└── api/
    └── chat.py                 # Issue #9
```

---

## Edge Cases & Error Handling

### Error Handling Matrix

| Scenario | Detection | Response | Recovery |
|----------|-----------|----------|----------|
| **LLM Timeout** | Try-except with timeout | Return empty intent (confidence=0.0) | User prompted to rephrase |
| **Invalid JSON** | Pydantic validation error | Use fallback JSON parser | Return partial data or empty intent |
| **Tool Failure** | Exception in tool | Return error string | Continue with available data |
| **Rate Limited** | HTTP 429 | Return error message | User retries later |
| **Ambiguous Destination** | Low confidence score | Ask clarification | Generate clarification questions |
| **Database Failure** | Connection error | Log error, retry | Don't lose itinerary |
| **Invalid User Input** | Validation error | Clear error message | Ask again |
| **API Key Invalid** | HTTP 401 | Return error message | Check environment config |

### Future Enhancement: Circuit Breaker Pattern

```python
# app/ai/tools/circuit_breaker.py - Future Enhancement
class CircuitBreaker:
    """Prevent cascading failures"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen("Service temporarily unavailable")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e
```

---

## API Contracts

### Request/Response Examples

**Chat Request:**
```json
POST /api/chat
{
  "message": "I want to visit Cebu for 3 days with my family",
  "session_id": "optional-existing-session-uuid"
}
```

**Clarification Response:**
```json
{
  "type": "clarification",
  "session_id": "uuid-here",
  "message": "Great start! Just a few more questions...",
  "questions": [
    {
      "id": "q_budget",
      "field": "budget",
      "type": "single_choice",
      "question": "What's your budget range?",
      "options": [
        {"id": "low", "label": "Budget-friendly", "emoji": "💰"}
      ],
      "required": true
    }
  ],
  "current_intent": {
    "destination": "Cebu",
    "days": 3,
    "companions": "family"
  },
  "progress": {
    "completed": 2,
    "total": 4,
    "percentage": 50
  }
}
```

**Itinerary Response:**
```json
{
  "type": "itinerary",
  "session_id": "uuid-here",
  "trip": {
    "id": 123,
    "title": "3-Day Family Trip to Cebu",
    "destination": "Cebu",
    "days": 3
  },
  "days": [...],
  "activities": [...],
  "summary": "A perfect family adventure...",
  "highlights": ["Kawasan Falls", "Cebu Safari"],
  "estimated_cost": {
    "total_min": 15000,
    "total_max": 30000,
    "currency": "PHP"
  },
  "tips": ["Book Kawasan Falls in advance"]
}
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_ai/test_intent_extraction.py

@pytest.mark.asyncio
async def test_extract_intent_complete():
    message = "I want to go to Boracay for 5 days with my partner, mid budget"
    intent = await extract_intent(message)
    
    assert intent.destination == "Boracay"
    assert intent.days == 5
    assert intent.companions == "couple"
    assert intent.budget == "mid"
    assert intent.is_complete()

@pytest.mark.asyncio
async def test_extract_intent_partial():
    message = "I want to visit Cebu"
    intent = await extract_intent(message)
    
    assert intent.destination == "Cebu"
    assert intent.days is None
    assert not intent.is_complete()
    assert "days" in intent.missing_info

@pytest.mark.asyncio
async def test_extract_intent_with_extra_notes():
    message = "Going to Palawan, vegetarian, love photography"
    intent = await extract_intent(message)
    
    assert intent.extra_notes.dietary_restrictions == "vegetarian"
    assert "photography" in intent.extra_notes.interests
```

### Integration Tests

```python
# tests/test_services/test_chat_service.py

@pytest.mark.asyncio
async def test_full_conversation_flow():
    service = ChatService()
    
    # Step 1: Initial message (incomplete)
    response1 = await service.process_message("I want to go to Cebu")
    assert response1.type == "clarification"
    
    # Step 2: Answer questions
    answers = {"q_budget": "mid", "q_days": "5", "q_companions": "family"}
    response2 = await service.submit_clarification(
        response1.session_id, 
        answers
    )
    
    # Step 3: Get itinerary
    assert response2.type == "itinerary"
    assert response2.trip.destination == "Cebu"
```

---

## Deployment Checklist

### Pre-deployment

- [x] All environment variables configured
- [ ] Database migrations applied
- [x] API keys validated (Gemini, Geoapify, OpenWeather)
- [ ] Rate limiting configured
- [ ] Logging setup (structured JSON)
- [ ] Health check endpoint added

### Future Enhancements

- [ ] Redis session management
- [ ] Redis connection pooling
- [ ] LLM response caching
- [ ] Tool retry logic with exponential backoff
- [ ] Circuit breaker pattern
- [ ] Caching layer for expensive API calls

### Performance

- [x] Async/await throughout
- [ ] Connection timeouts configured
- [ ] Database query optimization

### Monitoring

- [ ] Request/response logging
- [ ] Error tracking (Sentry)
- [ ] Performance metrics
- [ ] LLM token usage tracking
- [ ] Tool success/failure rates

### Security

- [x] Input validation (Pydantic)
- [ ] Rate limiting per user
- [ ] API key rotation
- [x] No secrets in logs
- [x] CORS configured

---

## Success Metrics

- **Response Time:**
  - Intent extraction: < 2 seconds
  - Itinerary generation: < 10 seconds
  - Clarification: < 1 second

- **Accuracy:**
  - Intent extraction: > 90% accuracy
  - Destination validation: 100% Philippines-only
  - Personalization compliance: > 95%

- **Reliability:**
  - Uptime: > 99%
  - Error rate: < 1%
  - Successful itinerary generation: > 95%

---

**Next Steps:**
1. ~~Start with Issue #8 (Foundation Tools)~~ ✅ COMPLETE
2. ~~Start with Issue #5 (Intent Extraction)~~ ✅ COMPLETE
3. Implement Issue #6 (Itinerary Generation Chain)
4. Implement Issue #7 (Follow-up Handler)
5. Implement Issue #9 (Chat Service & API)
6. Add Redis session management (Future Phase)

**Questions or adjustments needed?**
