# AI Prompt Templates Documentation

This document describes the prompt templates used in Atla's AI travel planning system.

## Overview

Atla uses LangChain with Google Gemini 2.5 Flash Lite for AI-powered travel planning. The system consists of three main chains:

1. **Intent Extraction Chain** - Extracts travel preferences from user messages
2. **Itinerary Generation Chain** - Creates detailed day-by-day itineraries
3. **Follow-up Handler Chain** - Handles clarifications, modifications, and suggestions

## Prompt Structure

Each prompt follows a consistent structure:

1. **System Context** - Who the AI is, its purpose
2. **Instructions** - Clear task description
3. **Input Format** - What data to expect
4. **Output Format** - Expected JSON structure
5. **Examples** - Few-shot learning for better performance
6. **Constraints** - Rules and limitations
7. **Output Instructions** - JSON formatting requirements

## Available Prompts

### 1. System Context (`system_context.txt`)

**Location:** `app/ai/prompts/system_context.txt`

Defines the core identity and behavioral guidelines for Atla:
- Core identity and specialization
- Knowledge base scope (Philippine travel)
- Behavioral guidelines (validation, practicality, safety)
- Budget guidelines in PHP
- Response style preferences
- Error handling approach

### 2. Intent Extraction (`intent_extraction.py`)

**Location:** `app/ai/prompts/intent_extraction.py`

**Purpose:** Extract travel preferences from natural language input.

**Key Features:**
- Extracts required fields: destination, days, budget, companions
- Extracts optional fields: travel_style, time_of_year
- Captures personalization: dietary_restrictions, must_visit, interests, etc.
- Includes confidence scoring (0.0-1.0)
- Validates destination is in Philippines

**Input Variables:**
- `{message}` - User's raw message
- `{context}` - Previous conversation context
- `{format_instructions}` - LangChain output parser instructions

**Example Input:**
```
"I want to go to Cebu for 5 days with my partner, mid budget"
```

**Example Output:**
```json
{
    "destination": "Cebu",
    "days": 5,
    "budget": "mid",
    "companions": "couple",
    "travel_style": ["beach", "food"],
    "time_of_year": null,
    "extra_notes": {},
    "confidence": 0.9
}
```

**Edge Cases Handled:**
- Missing information → Returns null values, sets confidence < 1.0
- Ambiguous destinations → Sets destination to null, confidence to low
- Non-Philippine destinations → Sets destination to null with note
- Vague time references → Accepts "next month", "summer", etc.

### 3. Itinerary Generation (`itinerary_generation.py`)

**Location:** `app/ai/prompts/itinerary_generation.py`

**Purpose:** Generate detailed day-by-day travel itineraries.

**Key Features:**
- Uses real-time place data from Geoapify
- Incorporates weather forecasts
- Budget-aware recommendations
- Companion-specific adjustments
- Detailed cost estimates in PHP

**Input Variables:**
- `{destination}` - Target destination
- `{days}` - Trip duration
- `{budget}` - low, mid, or luxury
- `{companions}` - solo, couple, family, or group
- `{travel_style}` - Comma-separated preferences
- `{time_of_year}` - When they plan to travel
- `{extra_notes}` - JSON with personalization details
- `{places_data}` - Results from place search API
- `{weather_data}` - Weather forecast data

**Output Structure:**
```json
{
    "summary": "Brief 2-3 sentence overview",
    "highlights": ["Top 3 highlights"],
    "days": [
        {
            "day_number": 1,
            "title": "Day 1: Title",
            "activities": [...],
            "meals": {...},
            "daily_tips": [...]
        }
    ],
    "estimated_cost": {...},
    "general_tips": [...],
    "packing_suggestions": [...]
}
```

**Budget Guidelines in Prompt:**
- **low:** Street food (100-300 PHP), jeepneys/tricycles, free parks
- **mid:** Mix of restaurants (300-800 PHP), some paid attractions
- **luxury:** Fine dining (1000+ PHP), private tours, premium experiences

**Companion Adjustments:**
- **solo:** Safe areas, social hostels, easy transport
- **couple:** Romantic spots, sunset viewpoints, nice restaurants
- **family:** Kid-friendly venues, shorter durations, accessible locations
- **group:** Group discounts, varied interests, large dining options

### 4. Follow-up Handler (`followup_handler.py`)

**Location:** `app/ai/prompts/followup_handler.py`

**Purpose:** Handle user follow-up messages during the planning process.

#### 4a. Type Detection

**Prompt:** `FOLLOWUP_TYPE_DETECTION_PROMPT`

Classifies user messages into categories:
- `clarification` - Answering questions
- `modification` - Changing existing plan
- `new_intent` - Completely new trip request
- `unsure` - Needs suggestions
- `unknown` - Unclear/unrelated

#### 4b. Modification Detection

**Prompt:** `MODIFICATION_DETECTION_PROMPT`

Extracts modification requests:
- **change** - Replace a value
- **add** - Add to a list
- **remove** - Remove from a list
- **extend** - Increase a value
- **shorten** - Decrease a value

Valid targets: destination, days, budget, companions, travel_style

#### 4c. Suggestion Extraction

**Prompt:** `SUGGESTION_EXTRACTION_PROMPT`

Extracts destination suggestions from web search results based on user preferences.

## Prompt Engineering Decisions

### Why Python Files Instead of .txt?

We use Python files (`.py`) for prompts instead of text files for several reasons:

1. **IDE Support** - Syntax highlighting, linting, type checking
2. **Version Control** - Better diffs in PRs
3. **Dynamic Content** - Can import constants, validate strings
4. **Testing** - Easier to test prompt outputs

### Few-Shot Learning

All prompts include examples to guide the LLM:

- Intent extraction includes sample JSON responses
- Itinerary generation shows expected output structure
- Follow-up handler includes modification examples

### JSON-Only Output

Prompts explicitly instruct the LLM to output only JSON:
- Reduces parsing complexity
- Ensures structured data
- Minimizes hallucinations

### Confidence Scoring

Intent extraction returns confidence scores (0.0-1.0):
- Helps determine if clarification is needed
- Guides follow-up question strategy
- Enables fallback to default values

### Budget-Aware Recommendations

Itinerary generation uses specific PHP amounts:
- Based on real Philippine pricing
- Differentiates between low/mid/luxury
- Includes accommodation, food, activities, transport

## Testing Prompts

Prompts are tested indirectly through chain tests:
- `test_intent_extraction.py` - Tests intent extraction outputs
- `test_followup_handler.py` - Tests follow-up handling
- Integration tests verify end-to-end prompt behavior

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-10 | Initial prompts for all 3 chains |
| 1.0.1 | 2026-03-10 | Added system_context.txt |

## Best Practices

1. **Be Specific** - Include exact field names and valid values
2. **Provide Examples** - Few-shot examples improve accuracy
3. **Set Boundaries** - Clear constraints reduce hallucinations
4. **Validate Output** - Always parse and validate JSON responses
5. **Handle Errors** - Graceful degradation when parsing fails

## Future Improvements

- Add prompt versioning with changelog
- Implement A/B testing for prompt variations
- Add prompt optimization based on user feedback
- Consider fine-tuning for better Philippine context
