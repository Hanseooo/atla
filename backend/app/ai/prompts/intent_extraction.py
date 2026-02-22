"""Prompt templates for AI chains."""

INTENT_EXTRACTION_PROMPT = """You are an expert travel planning assistant for the Philippines. Your job is to extract travel preferences from user messages.

Extract the following information from the user's message:

REQUIRED FIELDS:
- destination: Where they want to go (must be a location in the Philippines)
- days: Number of days for the trip (integer between 1-30)
- budget: Their budget level ("low", "mid", or "luxury")
- companions: Who they're traveling with ("solo", "couple", "family", or "group")

OPTIONAL FIELDS:
- travel_style: List of activity preferences ["adventure", "relaxation", "culture", "food", "beach", "nature", "nightlife"]
- time_of_year: When they plan to travel (e.g., "December 2024", "next month", "summer")

EXTRA NOTES (extract personalization details):
- dietary_restrictions: Any food restrictions mentioned
- accessibility_needs: Mobility or accessibility requirements
- must_visit: Specific places they mentioned wanting to see
- avoid: Things they want to avoid
- interests: Hobbies or interests mentioned
- special_occasion: If this is for a special event
- preferred_pace: How busy they want the trip ("relaxed", "moderate", "packed")
- accommodation_type: Hotel preference ("hotel", "resort", "hostel", "airbnb")
- budget_flexibility: "strict" or "flexible"
- transport_preference: "public", "private", or "rental"

USER MESSAGE: {message}

CURRENT CONTEXT: {context}

Respond ONLY with a valid JSON object in this exact format:
{{
    "destination": "Cebu",
    "days": 5,
    "budget": "mid",
    "companions": "couple",
    "travel_style": ["beach", "food", "relaxation"],
    "time_of_year": "December 2024",
    "extra_notes": {{
        "dietary_restrictions": "vegetarian",
        "must_visit": ["Kawasan Falls"],
        "interests": ["photography", "local food"]
    }},
    "confidence": 0.85
}}

Rules:
1. If information is missing, use null (not empty string)
2. For arrays, use empty array [] if none specified
3. Confidence score (0.0-1.0) based on how clear the message was
4. Destination MUST be in the Philippines - if unclear, set to null
5. Days must be integer between 1-30
6. Budget must be exactly "low", "mid", or "luxury"
7. Companions must be exactly "solo", "couple", "family", or "group"
8. Do not wrap the JSON in markdown code blocks

{format_instructions}"""

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
            {"id": "7", "label": "Week-long vacation (6-7 days)"},
            {"id": "10", "label": "Extended trip (8-10 days)"},
            {"id": "14", "label": "Two weeks+"},
        ],
    },
    "budget": {
        "question": "What's your budget range?",
        "type": "single_choice",
        "options": [
            {"id": "low", "label": "Budget-friendly", "description": "Under P5,000/day"},
            {"id": "mid", "label": "Moderate", "description": "P5,000-15,000/day"},
            {"id": "luxury", "label": "Luxury", "description": "P15,000+/day"},
        ],
    },
    "companions": {
        "question": "Who are you traveling with?",
        "type": "single_choice",
        "options": [
            {"id": "solo", "label": "Solo", "description": "Just me"},
            {"id": "couple", "label": "Partner", "description": "With my significant other"},
            {"id": "family", "label": "Family", "description": "With kids/relatives"},
            {"id": "group", "label": "Group", "description": "Friends or tour group"},
        ],
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
        ],
    },
    "time_of_year": {
        "question": "When are you planning to travel?",
        "type": "text",
        "placeholder": "e.g., December 2024, next month, summer",
    },
}

PROGRESS_MESSAGES = {
    0: "I'd love to help you plan your trip! Let me get some details first.",
    1: "Great start! Just a few more questions...",
    2: "Almost there! One more thing...",
    3: "Perfect! Let me put together your itinerary...",
}
