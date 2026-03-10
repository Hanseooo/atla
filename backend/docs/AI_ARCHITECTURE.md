# AI Architecture

This document describes the AI system architecture for Atla's travel planning capabilities.

## System Overview

Atla uses AI to power an intelligent travel planning experience. The system extracts user preferences from natural language, generates detailed itineraries, and handles follow-up conversations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│                    user message ───────▶                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    CHAT API ENDPOINTS                        ││
│  │  POST /api/chat, /{session_id}/clarify,                     ││
│  │  /{session_id}/generate-itinerary                            ││
│  └─────────────────────────┬───────────────────────────────────┘│
│                            │                                      │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   CHAT SERVICE                               ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  ││
│  │  │  Intent     │  │  Itinerary  │  │   Follow-up      │  ││
│  │  │  Extraction │  │  Generation │  │   Handler        │  ││
│  │  │  Chain      │  │  Chain       │  │   Chain          │  ││
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘  ││
│  └─────────┼─────────────────┼──────────────────┼────────────┘│
│            │                 │                  │               │
│            ▼                 ▼                  ▼               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    LANGCHAIN ORCHESTRATION                   ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ││
│  │  │ Gemini 2.5   │  │   Tools      │  │   Prompts      │  ││
│  │  │ Flash Lite   │  │ (Weather,    │  │   (Templates)  │  ││
│  │  │ (LLM)        │  │  Places,     │  │                │  ││
│  │  │              │  │  Search)     │  │                │  ││
│  │  └──────────────┘  └──────────────┘  └────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## AI Chains

### 1. Intent Extraction Chain

**Purpose:** Extract travel preferences from user messages

**Location:** `app/ai/chains/intent_extraction.py`

**Flow:**
```
User Message → LLM → Parse JSON → TravelIntent
```

**Extracted Fields:**
- `destination` (required): Philippines location
- `days` (required): 1-30
- `budget` (required): low, mid, luxury
- `companions` (required): solo, couple, family, group
- `travel_style` (optional): adventure, beach, culture, food, nature, relaxation, nightlife
- `time_of_year` (optional): When they plan to travel
- `extra_notes` (optional): dietary_restrictions, must_visit, interests, etc.

**Confidence Scoring:**
- Returns confidence (0.0-1.0) based on message clarity
- Low confidence triggers clarification questions

### 2. Itinerary Generation Chain

**Purpose:** Create detailed day-by-day travel plans

**Location:** `app/ai/chains/itinerary_generation.py`

**Flow:**
```
TravelIntent → Gather Context → LLM → Parse JSON → ItineraryOutput
                 │
                 ├─→ Geocode (get coordinates)
                 ├─→ Search Places (Geoapify)
                 └─→ Get Weather (Weather API)
```

**Output Structure:**
- `days_data`: List of TripDayData with activities
- `summary`: 2-3 sentence trip overview
- `highlights`: Top 3 attractions
- `estimated_cost`: Breakdown in PHP
- `tips`: General travel advice
- `packing_suggestions`: What to bring

### 3. Follow-up Handler Chain

**Purpose:** Handle clarifications, modifications, and suggestions

**Location:** `app/ai/chains/followup_handler.py`

**Flow:**
```
User Message → Detect Type → Handle Response
                   │
                   ├─→ clarification → Update intent
                   ├─→ modification → Apply changes
                   ├─→ unsure → Generate suggestions
                   └─→ unknown → Error response
```

**Types:**
- `clarification`: User answering questions
- `modification`: User changing plan details
- `new_intent`: Completely new trip request
- `unsure`: Needs destination suggestions
- `unknown`: Unclear message

## Tools Integration

### Available Tools

| Tool | Purpose | API |
|------|---------|-----|
| Geocode | Convert address to coordinates | Geoapify |
| Search Places | Find attractions, restaurants | Geoapify |
| Get Weather | Weather forecast | OpenWeather |
| Web Search | Additional information | DuckDuckGo |

### Tool Configuration

**Geoapify** (Places & Geocoding)
- Used for: Geocoding destinations, searching places
- Categories: tourism, catering, accommodation, entertainment

**OpenWeather** (Weather)
- Used for: Current weather and 5-day forecasts
- Requires `OPENWEATHER_API_KEY`

**DuckDuckGo** (Web Search)
- Used for: Fallback suggestions, additional info
- Free, no API key

## Data Flow

### Complete Chat Flow

```
1. User sends message
        │
        ▼
2. Check in-memory session store
        │
        ├─→ New session: Create empty TravelIntent
        │
        └─→ Existing session: Load TravelIntent from in-memory store
        │
        ▼
3. Extract intent from message (Intent Extraction Chain)
        │
        ▼
4. Check if intent is complete
        │
        ├─→ Incomplete: Generate clarification questions
        │      │
        │      └─→ Return ClarificationResponse
        │
        └─→ Complete: Continue to generation
        │
        ▼
5. Generate itinerary (Itinerary Generation Chain)
        │
        ▼
6. Save to database (via ChatService)
        │
        ▼
7. Return ItineraryResponse
```

### Follow-up Flow

```
1. User sends follow-up message
        │
        ▼
2. Load existing intent from in-memory store
        │
        ▼
3. Detect message type (Follow-up Handler Chain)
        │
        ├─→ clarification: Extract answers, update intent
        │      │
        │      └─→ Check if complete now
        │
        ├─→ modification: Apply changes to intent
        │      │
        │      ├─→ Regenerate if needed
        │      └─→ Return updated response
        │
        ├─→ unsure: Generate suggestions
        │      │
        │      └─→ Return with suggestions
        │
        └─→ unknown: Return error
        │
        ▼
4. Save updated session in memory
        │
        ▼
5. Return response
```

## Session Management

**Storage:** In-memory process store (`ChatService._sessions`)
**Key Format:** Session UUID
**TTL:** No TTL yet (manual cleanup strategy pending DB-backed sessions)

**Session Data:**
```json
{
  "session_id": "uuid",
  "intent": { ...TravelIntent... },
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## Error Handling

### Error Types

| Error | Cause | Handling |
|-------|-------|----------|
| IntentExtractionError | LLM fails to parse | Return empty intent with low confidence |
| ItineraryGenerationError | LLM fails or invalid JSON | Return error, suggest retry |
| GeocodingError | Invalid destination | Use default empty context |
| WeatherError | API unavailable | Continue without weather data |

### Graceful Degradation

- **Missing places data:** Continue with general recommendations
- **Missing weather:** Generate weather-agnostic itinerary
- **LLM timeout:** Return error with retry option
- **Invalid JSON:** Attempt multiple parsing strategies

## Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional (for enhanced features)
GEOAPIFY_API_KEY=your_geoapify_key
BRAVE_API_KEY=your_brave_search_key
OPENWEATHER_API_KEY=your_openweather_key
```

### Model Configuration

**Intent Extraction:**
- Model: gemini-2.5-flash-lite
- Temperature: 0.3 (more deterministic)

**Itinerary Generation:**
- Model: gemini-2.5-flash-lite
- Temperature: 0.7 (creative but controlled)

**Follow-up Handler:**
- Model: gemini-2.5-flash-lite
- Temperature: 0.3 (accurate parsing)

## Testing Strategy

### Unit Tests

- **Intent Extraction:** 95% coverage
- **Itinerary Generation:** 95% coverage
- **Follow-up Handler:** 87% coverage

### Mocking

All external APIs are mocked in tests:
- Gemini LLM: Mocked responses
- Tools: Mocked tool outputs
- Session store: in-memory mock

## Performance Considerations

1. **Concurrent Tool Calls:** Places and weather fetched in parallel
2. **Session Context:** Session data held in process memory
3. **Timeout:** LLM calls have 30s timeout
4. **Rate Limiting:** Consider adding for production

## Security

1. **API Keys:** Never exposed to frontend
2. **Input Validation:** Pydantic models validate all inputs
3. **Output Sanitization:** JSON parsing prevents injection
4. **Session Isolation:** User sessions isolated by session_id

## Future Improvements

1. **Streaming Responses:** Stream itinerary generation progress
2. **A/B Testing:** Compare prompt variations
3. **User Feedback:** Collect ratings for continuous improvement
4. **Fine-tuning:** Train custom model for Philippine travel
5. **Memory:** Long-term memory of past trips

---

**Related Documents:**
- [PROMPTS.md](../docs/PROMPTS.md) - Prompt templates
- [AI_TROUBLESHOOTING.md](./AI_TROUBLESHOOTING.md) - Common issues
