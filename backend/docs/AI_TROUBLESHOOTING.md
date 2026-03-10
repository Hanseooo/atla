# AI Troubleshooting Guide

This guide helps diagnose and resolve common issues with Atla's AI travel planning system.

## Common Errors

### 1. API Key Errors

#### Error: "API key not valid"

**Symptoms:**
```
400 INVALID_ARGUMENT: API key not valid. Please pass a valid API key.
```

**Cause:** Missing or invalid Google API key

**Solution:**
1. Check `.env` file has valid `GOOGLE_API_KEY`
2. Verify key has Generative Language API enabled
3. Get a new key from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

### 2. JSON Parsing Errors

#### Error: "Could not parse JSON from LLM response"

**Symptoms:**
```
ItineraryGenerationError: Could not parse JSON from LLM response
```

**Cause:** LLM returned malformed JSON

**Solution:**
- The chain has retry logic, should handle most cases
- Check prompt is correctly instructing for JSON-only output
- Verify LLM temperature isn't too high (>0.9)

---

### 3. Redis Connection Errors

#### Error: "Error 111 connecting to localhost:6379"

**Symptoms:**
```
ConnectionError: Error 111 connecting to localhost:6379
```

**Cause:** Redis not running

**Solution:**
1. Start Redis: `redis-server`
2. Or use Docker: `docker run -d -p 6379:6379 redis`
3. Update `REDIS_URL` in `.env` if using remote Redis

---

### 4. Intent Extraction Issues

#### Problem: Intent returns null for all fields

**Symptoms:**
```python
TravelIntent(destination=None, days=None, budget=None, companions=None)
confidence=0.0
```

**Cause:** User message unclear or LLM failed

**Solution:**
- Prompt user for more details
- Check confidence score - if < 0.5, ask clarifying questions
- Verify message contains travel-related keywords

---

#### Problem: Wrong destination extracted

**Symptoms:**
- User says "I want to go to Boracay"
- Intent shows "Bali" (or wrong place)

**Cause:** LLM hallucination or unclear message

**Solution:**
- Add "Philippines" context to prompt
- Ask user to confirm destination
- Use geocoding tool to validate

---

### 5. Itinerary Generation Issues

#### Problem: Itinerary has wrong number of days

**Symptoms:**
- User requests 5 days
- Generated itinerary has 3 days

**Cause:** LLM didn't follow the days parameter

**Solution:**
- Prompt explicitly states "Generate exactly {days} days"
- Check the raw LLM output
- May need lower temperature (0.5 or 0.3)

---

#### Problem: Activities not matching travel style

**Symptoms:**
- User wants "adventure" trips
- Itinerary shows mostly relaxing activities

**Cause:** Travel style not emphasized enough in prompt

**Solution:**
- Check prompt includes travel_style in personalization section
- Verify intent has correct travel_style values
- Consider adding more specific categories

---

#### Problem: Costs not in PHP

**Symptoms:**
- Activities show costs in USD or EUR instead of PHP

**Cause:** LLM defaulting to other currency

**Solution:**
- Prompt explicitly states "All costs must be in Philippine Peso (PHP)"
- Check LLM output for currency symbol
- If persistent, may need few-shot examples

---

### 6. Tool Errors

#### Error: Geocoding fails

**Symptoms:**
- "No places data available"
- Empty places_data in prompt

**Cause:**
- Invalid destination
- Geoapify API issue

**Solution:**
- Verify destination is valid Philippines location
- Check GEOAPIFY_API_KEY is set
- System continues gracefully without geocoding

---

#### Error: Weather API fails

**Symptoms:**
- "No weather data available"

**Cause:**
- Open-Meteo API unavailable
- Invalid coordinates

**Solution:**
- System continues without weather
- Weather is optional for itinerary generation
- No action needed unless persistent

---

### 7. Session Issues

#### Problem: Session not persisting

**Symptoms:**
- Each message starts new conversation
- Progress not saved

**Cause:**
- Redis not connected
- Session ID not being passed

**Solution:**
1. Verify Redis is running
2. Check session_id is included in requests
3. Verify Redis TTL not too short (default: 30 min)

---

#### Problem: Old session data

**Symptoms:**
- Seeing previous user's trip data

**Cause:**
- Session ID collision
- Redis not clearing old sessions

**Solution:**
1. Generate new session ID for each user
2. Clear Redis: `redis-cli FLUSHDB`
3. Check session expiry settings

---

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Chain Outputs

```python
# Add this before calling chain
import langchain
langchain.debug = True
```

### Test Intent Extraction Directly

```python
from app.ai.chains.intent_extraction import extract_intent

result = await extract_intent("I want to go to Cebu for 5 days")
print(result.model_dump())
```

### Test Itinerary Generation Directly

```python
from app.ai.chains.itinerary_generation import generate_itinerary
from app.ai.schemas.intent import TravelIntent

intent = TravelIntent(
    destination="Cebu",
    days=5,
    budget="mid",
    companions="couple"
)

result = await generate_itinerary(intent)
print(result.model_dump())
```

---

## Performance Issues

### Slow Response Times

**Possible Causes:**
1. LLM API latency
2. Tool calls (geocoding, weather)
3. Redis connection

**Solutions:**
1. Check API key quota
2. Increase timeout settings
3. Use connection pooling for Redis

### High Memory Usage

**Possible Causes:**
1. Large session history in Redis
2. Many concurrent requests
3. Large tool outputs

**Solutions:**
1. Limit conversation history (keep last 10 messages)
2. Implement request timeouts
3. Truncate tool outputs if too large

---

## Testing Issues

### Tests Failing Due to API Calls

**Problem:** Tests making real API calls

**Solution:** All tests should use mocks
```python
with patch("app.ai.chains.intent_extraction.LLMFactory.create_llm") as mock:
    # test code
```

### Coverage Too Low

**Target:** >80% for each chain

**Solution:**
- Add more unit tests for edge cases
- Test error handling paths
- Mock external dependencies

---

## Getting Help

###收集调试信息

When reporting issues, include:

1. **Error message** (full stack trace)
2. **User message** that caused the error
3. **Environment** (dev/prod)
4. **API keys** (masked)
5. **Logs** (with DEBUG level)

### 联系方式

- Check [GitHub Issues](https://github.com/atla-ai/atla/issues)
- Review [AI Architecture](./AI_ARCHITECTURE.md)
- Read [Prompt Documentation](./PROMPTS.md)

---

## Known Limitations

1. **Philippines Only:** System validates destinations are in Philippines
2. **Max 30 Days:** Trip duration limited to 30 days
3. **Budget Levels:** Only accepts "low", "mid", "luxury"
4. **Companion Types:** Only accepts "solo", "couple", "family", "group"
5. **Travel Styles:** Only accepts predefined set (adventure, beach, culture, food, nature, relaxation, nightlife)

---

## Error Codes Reference

| Code | Type | Description |
|------|------|-------------|
| EXTRACT_ERROR | Intent Extraction | Failed to parse user message |
| GENERATE_ERROR | Itinerary Generation | Failed to create itinerary |
| SESSION_ERROR | Session | Redis/session issue |
| VALIDATION_ERROR | Input | Invalid input data |
| API_ERROR | External | API key or quota issue |
